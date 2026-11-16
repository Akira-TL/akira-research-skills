"""Record a whole-directory move and rewrite every database path field once.

A move is given as Git top-level relative prefixes (``old_prefix`` ->
``new_prefix``; ``""`` is the top-level). The research root itself may move
with it (for example ``"" -> "research/"`` turns the repository root into a
``research/`` subdirectory root). Each stored project-relative path is first
expanded with the research root's old location, mapped through the move when
the file really moved, and finally written relative to the current research
root, so files that stayed outside the moved directory become ``../`` paths.
"""

from __future__ import annotations

import posixpath
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import research_db_ops.common as common
from research_db_core import ensure_research_gitignore, managed_gitignore_warning
from research_db_ops.completion.git import FreezeHistory
from research_db_support.git_layout import normalize_prefix
from research_db_support.storage import ResearchDbError, connect


# (table, column, extra SQL condition limiting rows to local paths)
PATH_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("artifacts", "path", ""),
    ("papers", "sidecar_path", ""),
    ("user_reading_events", "sidecar_path", ""),
    ("datasets", "provenance_path", ""),
    ("dataset_artifacts", "location", "storage_kind = 'local'"),
    ("studies", "provenance_path", ""),
    ("study_artifacts", "location", "storage_kind = 'local'"),
    ("analysis_runs", "analysis_path", ""),
    ("analysis_runs", "code_path", ""),
    ("analysis_artifacts", "path", ""),
    ("analysis_attempts", "config_path", ""),
    ("analysis_attempts", "output_path", ""),
    ("hypothesis_sets", "artifact_path", ""),
    ("research_designs", "artifact_path", ""),
    ("research_nodes", "artifact_path", ""),
    ("communication_products", "canonical_source_path", ""),
    ("communication_artifacts", "path", ""),
    ("communication_target_workspaces", "workspace_path", ""),
    ("communication_target_workspaces", "manifest_path", ""),
    ("communication_target_files", "path", ""),
    ("freeze_revisions", "path", ""),
)


@dataclass(frozen=True)
class Move:
    old_prefix: str
    new_prefix: str


class _PathMapper:
    def __init__(self, project_root: Path, history: FreezeHistory, commit: str, moves: list[Move]) -> None:
        self.layout = history.layout
        assert self.layout.toplevel is not None
        self.toplevel = self.layout.toplevel
        self.history = history
        self.commit = commit
        self.moves = sorted(moves, key=lambda move: len(move.old_prefix), reverse=True)
        self.old_project_prefix = self._backward(self.layout.prefix)

    def _backward(self, repo_prefix: str) -> str:
        for move in sorted(self.moves, key=lambda item: len(item.new_prefix), reverse=True):
            if repo_prefix.startswith(move.new_prefix):
                return move.old_prefix + repo_prefix[len(move.new_prefix):]
        return repo_prefix

    def _exists(self, repo_path: str) -> bool:
        if (self.toplevel / repo_path).exists():
            return True
        return self.history.repo_blob(self.commit, repo_path) is not None

    def _forward(self, old_repo: str) -> tuple[str, str]:
        move = next((item for item in self.moves if old_repo.startswith(item.old_prefix)), None)
        if move is None:
            return old_repo, "unchanged"
        candidate = move.new_prefix + old_repo[len(move.old_prefix):]
        if self._exists(old_repo):
            return old_repo, "stayed"
        if self._exists(candidate):
            return candidate, "moved"
        # Deleted or never-committed file: decide by its nearest existing parent directory.
        parent = posixpath.dirname(old_repo)
        floor = move.old_prefix.rstrip("/")
        while parent and parent != floor:
            if self._exists(parent):
                return old_repo, "stayed"
            if self._exists(move.new_prefix + parent[len(move.old_prefix):]):
                return candidate, "moved"
            parent = posixpath.dirname(parent)
        return old_repo, "unresolved"

    def map(self, value: str) -> tuple[str, str]:
        raw = value.strip()
        if not raw or Path(raw).is_absolute() or "://" in raw or raw.startswith("git:"):
            return value, "skipped"
        old_repo = posixpath.normpath(self.old_project_prefix + raw)
        if old_repo == ".." or old_repo.startswith("../"):
            return value, "skipped"
        new_repo, status = self._forward(old_repo)
        new_value = self.layout.project_path(new_repo)
        if raw.endswith("/") and not new_value.endswith("/"):
            new_value += "/"
        return new_value, status


def _parse_moves(bundle: dict[str, Any]) -> list[Move]:
    items = bundle.get("moves")
    if not isinstance(items, list) or not items:
        raise ResearchDbError("moves 必须是非空 JSON array，每项包含 old_prefix 与 new_prefix。")
    moves: list[Move] = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict) or "old_prefix" not in item or "new_prefix" not in item:
            raise ResearchDbError(f"move {index} 必须包含 old_prefix 与 new_prefix。")
        try:
            move = Move(normalize_prefix(str(item["old_prefix"])), normalize_prefix(str(item["new_prefix"])))
        except ValueError as exc:
            raise ResearchDbError(f"move {index}：{exc}") from exc
        if move.old_prefix == move.new_prefix:
            raise ResearchDbError(f"move {index} 的 old_prefix 与 new_prefix 相同。")
        moves.append(move)
    if len({move.old_prefix for move in moves}) != len(moves):
        raise ResearchDbError("同一次目录迁移中 old_prefix 不能重复。")
    return moves


def record_path_migration(project_root: Path, bundle: dict[str, Any]) -> dict[str, Any]:
    moves = _parse_moves(bundle)
    reason = common.text(bundle.get("reason"), required=True, field="reason")
    dry_run = bool(bundle.get("dry_run", False))
    history = FreezeHistory(project_root)
    if history.layout.toplevel is None:
        raise ResearchDbError("目录迁移需要科研项目位于 Git 仓库中。")
    commit = history.resolve(common.text(bundle.get("migration_commit")) or "HEAD")
    head = history.resolve("HEAD")
    if commit is None or head is None or not history.is_ancestor(commit, head):
        raise ResearchDbError("migration_commit 必须是当前 HEAD 历史中可解析的提交。")
    mapper = _PathMapper(project_root, history, commit, moves)

    rewrites: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    now = common.now()
    with connect(common.db_path(project_root)) as connection:
        tables = {
            str(row["name"])
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        if "path_migrations" not in tables:
            raise ResearchDbError("数据库尚无 path_migrations 表；先运行 research-db migrate。")
        for move in moves:
            if connection.execute(
                "SELECT 1 FROM path_migrations WHERE migration_commit = ? AND old_prefix = ?",
                (commit, move.old_prefix),
            ).fetchone():
                raise ResearchDbError(
                    f"目录迁移 '{move.old_prefix}' -> '{move.new_prefix}' @ {commit[:12]} 已登记，路径不会重复改写。"
                )
        connection.execute("BEGIN IMMEDIATE")
        try:
            for table, column, condition in PATH_FIELDS:
                if table not in tables:
                    continue
                where = f"{column} IS NOT NULL" + (f" AND {condition}" if condition else "")
                for row in connection.execute(f"SELECT rowid AS row_id, {column} AS value FROM {table} WHERE {where}"):
                    old_value = str(row["value"])
                    new_value, status = mapper.map(old_value)
                    if status == "unresolved":
                        unresolved.append({"table": table, "column": column, "path": old_value, "kept_as": new_value})
                    if new_value != old_value:
                        rewrites.append(
                            {"table": table, "column": column, "row_id": int(row["row_id"]),
                             "old": old_value, "new": new_value, "status": status}
                        )
            if not dry_run:
                for item in rewrites:
                    connection.execute(
                        f"UPDATE {item['table']} SET {item['column']} = ? WHERE rowid = ?",
                        (item["new"], item["row_id"]),
                    )
                for move in moves:
                    connection.execute(
                        """
                        INSERT INTO path_migrations(migration_commit, old_prefix, new_prefix, reason, created_at)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (commit, move.old_prefix, move.new_prefix, reason, now),
                    )
                connection.execute(
                    """
                    INSERT INTO change_log(timestamp, action, entity_type, entity_id, reason, summary)
                    VALUES (?, 'path_migration_recorded', 'path_migration', ?, ?, ?)
                    """,
                    (
                        now,
                        commit,
                        reason,
                        "moves="
                        + ", ".join(f"'{move.old_prefix}'->'{move.new_prefix}'" for move in moves)
                        + f"; rewritten_paths={len(rewrites)}; unresolved_paths={len(unresolved)}",
                    ),
                )
                connection.commit()
            else:
                connection.rollback()
        except Exception:
            connection.rollback()
            raise

    gitignore_updated = False if dry_run else ensure_research_gitignore(project_root)
    return {
        "ok": True,
        "dry_run": dry_run,
        "migration_commit": commit,
        "moves": [{"old_prefix": move.old_prefix, "new_prefix": move.new_prefix} for move in moves],
        "old_project_prefix": mapper.old_project_prefix,
        "project_prefix": history.layout.prefix,
        "rewritten_count": len(rewrites),
        "rewrites": rewrites,
        "unresolved": unresolved,
        "gitignore_updated": gitignore_updated,
        "gitignore_warning": managed_gitignore_warning(history.layout),
    }


def list_path_migrations(project_root: Path) -> dict[str, Any]:
    with connect(common.db_path(project_root)) as connection:
        rows = [dict(row) for row in connection.execute("SELECT * FROM path_migrations ORDER BY id")]
    return {"ok": True, "path_migrations": rows}

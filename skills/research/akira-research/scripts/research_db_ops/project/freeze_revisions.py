"""Record why a frozen Git-tracked object changed after its freeze commit."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import research_db_ops.common as common
from research_db_ops.completion.git import FreezeHistory
from research_db_support.storage import ResearchDbError, connect


REVISION_CATEGORIES = {"path_migration", "redundant_checksum_removal", "substantive"}


def _revision_items(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    items = bundle.get("revisions")
    if not isinstance(items, list) or not items:
        raise ResearchDbError("revisions 必须是非空 JSON array。")
    defaults = {key: bundle.get(key) for key in ("revision_commit", "category", "reason")}
    parsed: list[dict[str, Any]] = []
    for index, item in enumerate(items, start=1):
        if isinstance(item, str):
            item = {"path": item}
        if not isinstance(item, dict):
            raise ResearchDbError(f"revision {index} 必须是路径字符串或 JSON object。")
        merged = {**defaults, **{key: value for key, value in item.items() if value is not None}}
        path = common.text(merged.get("path"), required=True, field=f"revision {index} path")
        commit = common.text(
            merged.get("revision_commit"), required=True, field=f"revision {index} revision_commit"
        )
        category = common.enum_value(
            merged.get("category"), REVISION_CATEGORIES, default="", field=f"revision {index} category"
        )
        reason = common.text(merged.get("reason"), required=True, field=f"revision {index} reason")
        parsed.append({"path": path, "revision_commit": commit, "category": category, "reason": reason})
    return parsed


def record_freeze_revisions(project_root: Path, bundle: dict[str, Any]) -> dict[str, Any]:
    """Atomically record one or more (path, revision commit) revision notes.

    Every listed commit must be in the current history and must actually change
    the listed object's content; otherwise nothing is written.
    """

    items = _revision_items(bundle)
    history = FreezeHistory(project_root)
    head = history.resolve("HEAD")
    if head is None:
        raise ResearchDbError("科研项目尚无 Git commit，无法登记冻结后修订。")
    problems: list[str] = []
    for item in items:
        full = history.resolve(str(item["revision_commit"]))
        if full is None:
            problems.append(f"{item['path']}：revision_commit 不是可解析的 Git commit：{item['revision_commit']}")
            continue
        item["revision_commit"] = full
        if not history.is_ancestor(full, head):
            problems.append(f"{item['path']}：{full[:12]} 不在当前 HEAD 历史中。")
            continue
        if history.layout.repo_path(str(item["path"])) is None:
            problems.append(f"{item['path']}：路径不在科研项目所在 Git 仓库内。")
            continue
        parents = history.parents(full)
        before = history.blob(parents[0], item["path"]) if parents else None
        if history.blob(full, item["path"]) == before:
            problems.append(f"{item['path']}：{full[:12]} 没有改变该对象内容，无需登记修订。")
    if problems:
        raise ResearchDbError("冻结后修订登记失败：" + " | ".join(problems))

    now = common.now()
    recorded: list[dict[str, Any]] = []
    with connect(common.db_path(project_root)) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            for item in items:
                existing = connection.execute(
                    "SELECT category, reason FROM freeze_revisions WHERE path = ? AND revision_commit = ?",
                    (item["path"], item["revision_commit"]),
                ).fetchone()
                if existing is not None:
                    if (str(existing["category"]), str(existing["reason"])) != (item["category"], item["reason"]):
                        raise ResearchDbError(
                            f"{item['path']} @ {item['revision_commit'][:12]} 已有不同的修订说明，不可静默改写。"
                        )
                    continue
                cursor = connection.execute(
                    """
                    INSERT INTO freeze_revisions(path, revision_commit, category, reason, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (item["path"], item["revision_commit"], item["category"], item["reason"], now),
                )
                connection.execute(
                    """
                    INSERT INTO change_log(timestamp, action, entity_type, entity_id, reason, summary)
                    VALUES (?, 'freeze_revision_recorded', 'freeze_revision', ?, ?, ?)
                    """,
                    (
                        now,
                        str(cursor.lastrowid),
                        item["reason"],
                        f"path={item['path']}; commit={item['revision_commit']}; category={item['category']}",
                    ),
                )
                recorded.append(item)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
    return {"ok": True, "recorded": recorded, "already_recorded": len(items) - len(recorded)}


def list_freeze_revisions(project_root: Path, *, pending: bool = False, limit: int = 500) -> dict[str, Any]:
    with connect(common.db_path(project_root)) as connection:
        rows = [
            dict(row)
            for row in connection.execute(
                "SELECT * FROM freeze_revisions ORDER BY id LIMIT ?", (limit,)
            )
        ]
    result: dict[str, Any] = {"ok": True, "revisions": rows}
    if pending:
        from research_db_ops.completion import validate_completion

        git_info = validate_completion(project_root).get("git", {})
        result["pending"] = git_info.get("unrecorded_frozen_changes", [])
    return result


_CHECKSUM_TEXT_RE = re.compile(r"[0-9a-fA-F]{64}")
_TRACKED_ARTIFACT_QUERIES = (
    (
        "dataset_artifacts",
        "SELECT a.id, d.slug AS owner, a.location AS path, a.version FROM dataset_artifacts a "
        "JOIN datasets d ON d.id = a.dataset_id WHERE a.git_tracking = 'required' AND a.version IS NOT NULL "
        "ORDER BY a.id",
    ),
    (
        "study_artifacts",
        "SELECT a.id, s.slug AS owner, a.location AS path, a.version FROM study_artifacts a "
        "JOIN studies s ON s.id = a.study_id WHERE a.git_tracking = 'required' AND a.version IS NOT NULL "
        "ORDER BY a.id",
    ),
)


def list_tracked_artifact_checksums(project_root: Path) -> dict[str, Any]:
    """Read-only report: Git-tracked artifacts whose free-text version still carries a SHA256.

    Git-tracked artifacts are frozen by commit + path, so such checksums are
    redundant historical text the project may clean up; nothing is changed here.
    """

    rows: list[dict[str, Any]] = []
    with connect(common.db_path(project_root)) as connection:
        for table, query in _TRACKED_ARTIFACT_QUERIES:
            for row in connection.execute(query):
                if _CHECKSUM_TEXT_RE.search(str(row["version"])):
                    rows.append({"table": table, **dict(row)})
    return {"ok": True, "count": len(rows), "artifacts": rows}

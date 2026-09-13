from __future__ import annotations

import sqlite3
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from research_db_support.schema import latest_version
from research_db_support.storage import connect, database_path

from ..git import commit_has_path, path_changed_after, run_git


def legacy_baseline_commit(project_root: Path, meta_key: str) -> str | None:
    db_path = database_path(project_root)
    if not db_path.exists():
        return None
    with connect(db_path) as connection:
        try:
            row = connection.execute(
                "SELECT value FROM meta WHERE key = ?",
                (meta_key,),
            ).fetchone()
        except sqlite3.OperationalError:
            return None
    value = str(row["value"]).strip() if row else ""
    return value or None


def schema_version_at_commit(project_root: Path, commit: str) -> int | None:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(project_root),
            "show",
            f"{commit}:.research/research.sqlite",
        ],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout:
        return None
    with tempfile.NamedTemporaryFile(suffix=".sqlite") as handle:
        handle.write(result.stdout)
        handle.flush()
        try:
            with sqlite3.connect(handle.name) as connection:
                version = int(connection.execute("PRAGMA user_version").fetchone()[0])
                if version:
                    return version
                row = connection.execute(
                    "SELECT value FROM meta WHERE key = 'schema_version'"
                ).fetchone()
                return int(row[0]) if row else None
        except (sqlite3.DatabaseError, ValueError, TypeError):
            return None


def validate_legacy_baseline(
    project_root: Path,
    baseline_commit: str | None,
    *,
    invalid_reason: str,
    introduced_in_schema: int | None = None,
) -> tuple[str | None, dict[str, Any] | None]:
    if not baseline_commit:
        return None, None
    if run_git(
        project_root, "merge-base", "--is-ancestor", baseline_commit, "HEAD"
    ).returncode != 0:
        return None, {
            "reason": invalid_reason,
            "baseline_commit": baseline_commit,
            "detail": "legacy baseline 不是当前 HEAD 的祖先。",
        }
    baseline_schema_version = schema_version_at_commit(project_root, baseline_commit)
    current_schema_version = latest_version()
    schema_ceiling = introduced_in_schema or current_schema_version
    if baseline_schema_version is None or baseline_schema_version >= schema_ceiling:
        return None, {
            "reason": invalid_reason,
            "baseline_commit": baseline_commit,
            "baseline_schema_version": baseline_schema_version,
            "current_schema_version": current_schema_version,
            "introduced_in_schema": introduced_in_schema,
            "detail": (
                "legacy baseline 只允许由真实 schema migration 记录；baseline commit 中的数据库 "
                + (
                    f"schema 必须低于该兼容契约启用版本 v{introduced_in_schema}。"
                    if introduced_in_schema is not None
                    else "schema 必须低于当前版本。"
                )
            ),
        }
    return baseline_commit, None


def path_is_unchanged_since_baseline(
    project_root: Path,
    path: Path,
    baseline_commit: str | None,
) -> bool:
    if not baseline_commit:
        return False
    try:
        relative_path = path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return False
    if run_git(
        project_root, "merge-base", "--is-ancestor", baseline_commit, "HEAD"
    ).returncode != 0:
        return False
    if not commit_has_path(project_root, baseline_commit, relative_path):
        return False
    if path_changed_after(project_root, baseline_commit, relative_path):
        return False
    return run_git(
        project_root, "diff", "--quiet", baseline_commit, "--", relative_path
    ).returncode == 0

from __future__ import annotations

from pathlib import Path

from research_db_support.git_layout import commit_has_path, run_git

__all__ = [
    "commit_has_path",
    "first_path_change_after",
    "path_changed_after",
    "run_git",
]


def path_changed_after(project_root: Path, commit: str, path: str) -> bool:
    result = run_git(project_root, "log", "--format=%H", f"{commit}..HEAD", "--", path)
    return result.returncode != 0 or bool(result.stdout.strip())


def first_path_change_after(project_root: Path, commit: str, path: str) -> str | None:
    result = run_git(
        project_root,
        "log",
        "--reverse",
        "--format=%H",
        f"{commit}..HEAD",
        "--",
        path,
    )
    if result.returncode != 0:
        return None
    return next((line.strip() for line in result.stdout.splitlines() if line.strip()), None)

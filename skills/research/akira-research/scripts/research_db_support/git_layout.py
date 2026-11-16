"""Map research-project paths onto the Git repository that contains them.

The research project root (the directory holding ``RESEARCH.md`` and
``.research/``) may be the Git top-level or any subdirectory of it. Database
path fields stay relative to the research project root and may point outside
it (``../scripts/run.py``) as long as they stay inside the Git work tree. Git
object specs such as ``<commit>:<path>`` are always top-level relative, so every
lookup goes through :class:`GitLayout`.
"""

from __future__ import annotations

import os
import posixpath
import subprocess
from dataclasses import dataclass
from pathlib import Path


def run_git(
    project_root: Path,
    *args: str,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(project_root), *args],
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def normalize_prefix(value: str) -> str:
    """Return a top-level relative directory prefix: ``""`` or ``"dir/sub/"``."""

    raw = value.strip().replace("\\", "/")
    while raw.startswith("./"):
        raw = raw[2:]
    raw = raw.strip("/")
    if not raw or raw == ".":
        return ""
    normalized = posixpath.normpath(raw)
    if normalized.startswith("../") or normalized == "..":
        raise ValueError(f"prefix 不能越出 Git 仓库：{value}")
    return normalized + "/"


@dataclass(frozen=True)
class GitLayout:
    project_root: Path
    toplevel: Path | None
    prefix: str

    @property
    def in_repository(self) -> bool:
        return self.toplevel is not None

    def repo_path(self, project_path: str) -> str | None:
        """Convert a project-relative path to a top-level relative path."""

        if self.toplevel is None:
            return None
        raw = str(project_path).strip().replace("\\", "/")
        if not raw:
            return None
        if Path(raw).is_absolute():
            try:
                raw = Path(raw).resolve().relative_to(self.toplevel).as_posix()
            except ValueError:
                return None
            joined = raw
        else:
            joined = self.prefix + raw
        normalized = posixpath.normpath(joined)
        if normalized in {".", ""} or normalized == ".." or normalized.startswith("../"):
            return None
        return normalized

    def project_path(self, repo_path: str) -> str:
        """Express a top-level relative path relative to the research project root."""

        start = self.prefix.rstrip("/") or "."
        return posixpath.relpath(repo_path, start)

    def object_spec(self, commit: str, project_path: str) -> str | None:
        repo_path = self.repo_path(project_path)
        return None if repo_path is None else f"{commit}:{repo_path}"


def git_layout(project_root: Path) -> GitLayout:
    root = project_root.resolve()
    top = run_git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or not top.stdout.strip():
        return GitLayout(project_root=root, toplevel=None, prefix="")
    toplevel = Path(top.stdout.strip()).resolve()
    try:
        relative = root.relative_to(toplevel).as_posix()
    except ValueError:
        return GitLayout(project_root=root, toplevel=None, prefix="")
    return GitLayout(project_root=root, toplevel=toplevel, prefix=normalize_prefix(relative))


def path_boundary(project_root: Path) -> Path:
    """Directory that project paths may reach: the Git top-level, else the research root."""

    layout = git_layout(project_root)
    return layout.toplevel or layout.project_root


def project_relative(project_root: Path, path: Path) -> str:
    """Project-relative POSIX path; paths outside the project use ``../`` segments."""

    resolved = path.resolve()
    root = project_root.resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return Path(os.path.relpath(resolved, root)).as_posix()


def commit_has_path(project_root: Path, commit: str, project_path: str) -> bool:
    spec = git_layout(project_root).object_spec(commit, project_path)
    if spec is None:
        return False
    return run_git(project_root, "cat-file", "-e", spec).returncode == 0


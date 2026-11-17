"""History of frozen research objects after their freeze commit.

A frozen Git-tracked object is identified by its freeze commit and path. Later
commits may still change it; such a change passes the completion gate only
when ``freeze_revisions`` records it (path + revision commit + category +
reason). Unrecorded changes are reported with their commits so they can be
recorded or reverted. Content is compared by Git blob, so commits that touch a
path without changing its content are not changes.
"""

from __future__ import annotations

import sqlite3
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

from research_db_support.git_layout import GitLayout, commit_has_path, git_layout, run_git
from research_db_support.storage import connect, database_path


# Revision categories that let a post-freeze change pass. A ``substantive``
# revision is recorded for provenance but keeps blocking.
PASSING_REVISION_CATEGORIES = frozenset({"path_migration", "redundant_checksum_removal"})


@dataclass(frozen=True)
class PathMigration:
    commit: str
    old_prefix: str
    new_prefix: str

    def to_old(self, repo_path: str) -> str | None:
        if not repo_path.startswith(self.new_prefix):
            return None
        return self.old_prefix + repo_path[len(self.new_prefix):]


@dataclass
class FrozenChange:
    path: str
    anchor: str
    since: str
    commits: list[str] = field(default_factory=list)
    substantive_commits: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "anchor": self.anchor,
            "since": self.since,
            "commits": self.commits,
            "substantive_commits": self.substantive_commits,
        }

    def blocker_entry(self) -> dict[str, Any]:
        return {"path": self.path, "commits": self.commits, "substantive_commits": self.substantive_commits}


class FreezeHistory:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.layout: GitLayout = git_layout(project_root)
        self._commits: dict[str, str | None] = {}
        self._ancestry: dict[tuple[str, str], bool] = {}
        self._blobs: dict[tuple[str, str], str | None] = {}
        self._changes: dict[tuple[str, str], list[str]] = {}
        self.blocked: dict[tuple[str, str, str], FrozenChange] = {}
        self.reverted: dict[tuple[str, str, str], FrozenChange] = {}
        self.applied: dict[tuple[str, str], dict[str, Any]] = {}
        self._revision_rows: dict[tuple[str, str], dict[str, Any]] = {}
        self.migrations: list[PathMigration] = []
        self._load_revisions()
        self._load_migrations()

    # -- database --------------------------------------------------------------

    def _load_revisions(self) -> None:
        db_path = database_path(self.project_root)
        if not db_path.exists():
            return
        with connect(db_path) as connection:
            try:
                rows = connection.execute(
                    "SELECT path, revision_commit, category, reason FROM freeze_revisions ORDER BY id"
                ).fetchall()
            except sqlite3.OperationalError:
                return
        for row in rows:
            repo_path = self.layout.repo_path(str(row["path"]))
            if repo_path is None:
                continue
            key = (repo_path, str(row["revision_commit"]))
            self._revision_rows[key] = {
                "path": str(row["path"]),
                "revision_commit": str(row["revision_commit"]),
                "category": str(row["category"]),
                "reason": str(row["reason"]),
            }

    def _load_migrations(self) -> None:
        db_path = database_path(self.project_root)
        if not db_path.exists():
            return
        with connect(db_path) as connection:
            try:
                rows = connection.execute(
                    "SELECT migration_commit, old_prefix, new_prefix FROM path_migrations ORDER BY id"
                ).fetchall()
            except sqlite3.OperationalError:
                return
        head = self.resolve("HEAD")
        distance: dict[PathMigration, int] = {}
        for row in rows:
            commit = self.resolve(str(row["migration_commit"]))
            if commit is None or head is None or not self.is_ancestor(commit, head):
                continue
            migration = PathMigration(commit, str(row["old_prefix"]), str(row["new_prefix"]))
            count = run_git(self.project_root, "rev-list", "--count", f"{commit}..{head}")
            distance[migration] = int(count.stdout.strip() or 0)
        # Newest first, so chained moves are undone in reverse order.
        self.migrations = sorted(distance, key=lambda item: (distance[item], -len(item.new_prefix)))

    # -- git primitives --------------------------------------------------------

    def resolve(self, ref: str) -> str | None:
        if ref not in self._commits:
            result = run_git(self.project_root, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
            self._commits[ref] = result.stdout.strip() if result.returncode == 0 else None
        return self._commits[ref]

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        key = (ancestor, descendant)
        if key not in self._ancestry:
            self._ancestry[key] = (
                run_git(self.project_root, "merge-base", "--is-ancestor", ancestor, descendant).returncode == 0
            )
        return self._ancestry[key]

    def parents(self, commit: str) -> list[str]:
        result = run_git(self.project_root, "rev-list", "--parents", "-n", "1", commit)
        return result.stdout.split()[1:] if result.returncode == 0 else []

    def path_at(self, commit: str, project_path: str) -> str | None:
        """Top-level relative path the object had in ``commit``.

        The current path is mapped back through every recorded directory
        migration that ``commit`` predates.
        """

        repo_path = self.layout.repo_path(project_path)
        if repo_path is None or not self.migrations:
            return repo_path
        full = self.resolve(commit)
        if full is None:
            return repo_path
        for migration in self.migrations:
            if self.is_ancestor(migration.commit, full):
                continue
            older = migration.to_old(repo_path)
            if older is not None:
                repo_path = older
        return repo_path

    def repo_blob(self, commit: str, repo_path: str | None) -> str | None:
        """Blob (or tree) id of a top-level relative path in ``commit``."""

        return self._blob(commit, repo_path)

    def _blob(self, commit: str, repo_path: str | None) -> str | None:
        if repo_path is None:
            return None
        key = (commit, repo_path)
        if key not in self._blobs:
            result = run_git(self.project_root, "rev-parse", "--verify", "--quiet", f"{commit}:{repo_path}")
            self._blobs[key] = result.stdout.strip() if result.returncode == 0 else None
        return self._blobs[key]

    def blob(self, commit: str, project_path: str) -> str | None:
        return self._blob(commit, self.path_at(commit, project_path))

    def has_path(self, commit: str, project_path: str) -> bool:
        return self.blob(commit, project_path) is not None

    def read(self, commit: str, project_path: str) -> bytes | None:
        repo_path = self.path_at(commit, project_path)
        if repo_path is None:
            return None
        result = subprocess.run(
            ["git", "-C", str(self.project_root), "show", f"{commit}:{repo_path}"],
            capture_output=True,
            check=False,
        )
        return result.stdout if result.returncode == 0 else None

    def _history_paths(self, since: str, project_path: str) -> list[str]:
        paths = {self.path_at(since, project_path), self.path_at("HEAD", project_path)}
        for migration in self.migrations:
            for parent in self.parents(migration.commit):
                paths.add(self.path_at(parent, project_path))
        return sorted(path for path in paths if path is not None)

    # -- change detection ------------------------------------------------------

    def iter_content_changes(self, since: str, project_path: str) -> Iterator[str]:
        """Commits after ``since`` (oldest first) that changed the object's content.

        The list is cached only after a full pass, so callers may stop early.
        """

        key = (since, project_path)
        if key in self._changes:
            yield from self._changes[key]
            return
        paths = self._history_paths(since, project_path)
        changes: list[str] = []
        if paths:
            result = run_git(
                self.project_root,
                "log",
                "--reverse",
                "--full-history",
                "--no-merges",
                "--format=%H %P",
                f"{since}..HEAD",
                "--",
                *(f":(top){path}" for path in paths),
            )
            for line in result.stdout.splitlines():
                parts = line.split()
                if not parts:
                    continue
                commit, parents = parts[0], parts[1:]
                after = self.blob(commit, project_path)
                before = self.blob(parents[0], project_path) if parents else None
                if after != before:
                    changes.append(commit)
                    yield commit
        self._changes[key] = changes

    def content_changes(self, since: str, project_path: str) -> list[str]:
        return list(self.iter_content_changes(since, project_path))

    def net_changed(self, since: str, project_path: str) -> bool:
        return self.blob(since, project_path) != self.blob("HEAD", project_path)

    def _revision_for(self, project_path: str, commit: str) -> dict[str, Any] | None:
        repo_path = self.layout.repo_path(project_path)
        return None if repo_path is None else self._revision_rows.get((repo_path, commit))

    def blocking_changes(
        self,
        since: str,
        project_path: str,
        *,
        anchor: str,
        report: bool = True,
    ) -> FrozenChange | None:
        """Return ``None`` when the frozen object passes, else the commits that block it.

        An object whose current content is byte-identical to the frozen version
        passes; intermediate commits that changed and restored it are only
        listed in the run summary (``reverted_frozen_changes``). Otherwise every
        content-changing commit needs a recorded passing revision
        (``PASSING_REVISION_CATEGORIES``). Unrecorded commits are listed in
        ``commits``; commits recorded as ``substantive`` stay blocking and are
        listed in ``substantive_commits`` because they need a new Analysis or
        Design rather than a revision note. With ``report=False`` the check
        stops at the first blocking commit and nothing is added to the run
        summary (used for legacy compatibility, where living documents are
        expected to change).
        """

        change = FrozenChange(path=project_path, anchor=anchor, since=since)
        if not self.net_changed(since, project_path):
            if report:
                change.commits = self.content_changes(since, project_path)
                if change.commits:
                    self.reverted[(project_path, anchor, since)] = change
            return None
        for commit in self.iter_content_changes(since, project_path):
            revision = self._revision_for(project_path, commit)
            if revision is not None and revision["category"] in PASSING_REVISION_CATEGORIES:
                if report:
                    self.applied[(revision["path"], commit)] = revision
                continue
            (change.commits if revision is None else change.substantive_commits).append(commit)
            if not report:
                return change
        if not change.commits and not change.substantive_commits:
            # Net content differs, yet every change commit is a recorded passing revision.
            if self.content_changes(since, project_path):
                return None
        if report:
            self.blocked[(project_path, anchor, since)] = change
        return change

    def first_change(self, since: str, project_path: str) -> str | None:
        return next(self.iter_content_changes(since, project_path), None)

    def summary(self) -> dict[str, Any]:
        def entry(change: FrozenChange, commits: list[str]) -> dict[str, Any]:
            return {"path": change.path, "anchor": change.anchor, "since": change.since, "commits": commits}

        blocked = list(self.blocked.values())
        return {
            "unrecorded_frozen_changes": [
                entry(change, change.commits)
                for change in blocked
                if change.commits or not change.substantive_commits
            ],
            "substantive_frozen_changes": [
                entry(change, change.substantive_commits) for change in blocked if change.substantive_commits
            ],
            "reverted_frozen_changes": [entry(change, change.commits) for change in self.reverted.values()],
            "applied_freeze_revisions": list(self.applied.values()),
        }


_SESSIONS: dict[str, FreezeHistory] = {}


@contextmanager
def freeze_history_session(project_root: Path) -> Iterator[FreezeHistory]:
    """Share one history (caches, recorded/unrecorded changes) across a completion run."""

    key = str(project_root.resolve())
    owner = key not in _SESSIONS
    if owner:
        _SESSIONS[key] = FreezeHistory(project_root)
    try:
        yield _SESSIONS[key]
    finally:
        if owner:
            _SESSIONS.pop(key, None)


def freeze_history(project_root: Path) -> FreezeHistory:
    return _SESSIONS.get(str(project_root.resolve())) or FreezeHistory(project_root)


__all__ = [
    "FreezeHistory",
    "PASSING_REVISION_CATEGORIES",
    "PathMigration",
    "FrozenChange",
    "commit_has_path",
    "freeze_history",
    "freeze_history_session",
    "run_git",
]

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

from research_db_support.git_layout import git_layout, project_relative
from research_db_support.storage import ResearchDbError, database_path


GIT_TRACKING = {"required", "not_required"}
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_timestamp(value: object, *, field: str) -> datetime:
    raw = text(value, required=True, field=field)
    assert raw is not None
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ResearchDbError(f"{field} 必须是 ISO 8601 时间戳。") from exc
    if parsed.tzinfo is None:
        raise ResearchDbError(f"{field} 必须包含时区偏移。")
    return parsed.astimezone(timezone.utc)


def db_path(project_root: Path) -> Path:
    path = database_path(project_root)
    if not path.exists():
        raise ResearchDbError("research.sqlite 不存在；先运行 research-db init。")
    return path


def text(value: object, *, required: bool = False, field: str = "字段") -> str | None:
    if value is None:
        if required:
            raise ResearchDbError(f"{field} 不能为空。")
        return None
    result = str(value).strip()
    if not result and required:
        raise ResearchDbError(f"{field} 不能为空。")
    return result or None


def enum_value(value: object, allowed: set[str], *, default: str, field: str) -> str:
    result = text(value) or default
    if result not in allowed:
        raise ResearchDbError(f"{field} 必须是：{', '.join(sorted(allowed))}")
    return result


def slug(value: object, *, field: str = "slug") -> str:
    result = text(value, required=True, field=field)
    assert result is not None
    if not _SLUG_RE.fullmatch(result):
        raise ResearchDbError(f"{field} 必须使用 lowercase kebab-case。")
    return result


def local_path(
    project_root: Path,
    value: object,
    *,
    field: str,
    require_file: bool = False,
) -> str:
    raw = text(value, required=True, field=field)
    assert raw is not None
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = project_root / path
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(project_root.resolve()).as_posix()
    except ValueError as exc:
        layout = git_layout(project_root)
        if layout.toplevel is None:
            raise ResearchDbError(f"{field} 必须位于科研项目目录内：{resolved}") from exc
        try:
            resolved.relative_to(layout.toplevel)
        except ValueError:
            raise ResearchDbError(
                f"{field} 必须位于科研项目目录或其所在 Git 仓库内：{resolved}"
            ) from exc
        relative = project_relative(project_root, resolved)
    exists = resolved.is_file() if require_file else resolved.exists()
    if not exists:
        raise ResearchDbError(f"{field} 指向的文件不存在：{relative}")
    return relative


ANALYSIS_CODE_PREFIXES = ("scripts/analyses/", "src/")


def is_analysis_code_path(project_root: Path, path: str) -> bool:
    """Analysis code lives in scripts/analyses/ or src/ of the research root or of the Git top-level."""

    if path.startswith(ANALYSIS_CODE_PREFIXES):
        return True
    repo_path = git_layout(project_root).repo_path(path) if path.startswith("../") else None
    return repo_path is not None and repo_path.startswith(ANALYSIS_CODE_PREFIXES)


def tracking(value: object, *, default: str = "required") -> str:
    return enum_value(value, GIT_TRACKING, default=default, field="git_tracking")


_SHA256_RE = re.compile(r"^(?:sha256:)?([0-9a-fA-F]{64})$")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def untracked_sha256(
    project_root: Path,
    value: object,
    *,
    git_tracking: str,
    location: str | None,
    field: str,
) -> str | None:
    """Validate the single content checksum allowed for artifacts outside Git.

    Git-tracked artifacts are frozen by commit + path, so a checksum is rejected
    as redundant. For local untracked files the recorded value must match the
    current file content.
    """

    raw = text(value)
    if raw is None:
        return None
    if git_tracking == "required":
        raise ResearchDbError(
            f"{field}：Git 跟踪的 artifact 由提交号 + 路径冻结，不记录文件校验值；"
            "sha256 只用于 git_tracking=not_required 或外部存储的对象。"
        )
    match = _SHA256_RE.fullmatch(raw)
    if match is None:
        raise ResearchDbError(f"{field} 必须是 64 位十六进制 SHA256（可带 sha256: 前缀）。")
    digest = match.group(1).lower()
    if location is not None:
        path = Path(location)
        path = path if path.is_absolute() else project_root / path
        if path.is_file() and file_sha256(path) != digest:
            raise ResearchDbError(f"{field} 与当前文件内容不一致：{location}")
    return digest


def attach_sha256(connection, table: str, row_id: int, digest: str | None, *, label: str) -> None:
    """Fill an artifact checksum once; an existing different checksum is never overwritten."""

    if digest is None:
        return
    row = connection.execute(f"SELECT sha256 FROM {table} WHERE id = ?", (row_id,)).fetchone()
    if row is None:
        return
    if row["sha256"] is None:
        connection.execute(f"UPDATE {table} SET sha256 = ? WHERE id = ?", (digest, row_id))
    elif str(row["sha256"]) != digest:
        raise ResearchDbError(f"{label} 已登记不同的 sha256，不可静默改写。")

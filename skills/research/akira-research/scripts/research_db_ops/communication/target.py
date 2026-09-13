from __future__ import annotations

import json
import re
import subprocess
import unicodedata
from pathlib import Path
from typing import Any

from research_db_support.storage import ResearchDbError
import research_db_ops.common as common


JOURNAL_CODE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]{0,15}$")
TARGET_TEMPLATE_STATUSES = {"provided", "not_provided", "not_applicable"}
COMPOSITE_OUTPUT_SUFFIXES = {
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".pdf",
    ".odt",
    ".ods",
    ".odp",
}


def journal_code(value: object) -> str:
    code = common.text(value, required=True, field="journal code")
    assert code is not None
    if not JOURNAL_CODE_RE.fullmatch(code):
        raise ResearchDbError(
            "journal code 必须以字母开头，只包含字母和数字，且长度不超过 16；例如 NC 或 iMeta。"
        )
    return code


def journal_name_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return "".join(char for char in normalized if char.isalnum())


def workspace_path(slug: str, code: str) -> str:
    return f"communication/{slug}/{code}-release"


def manifest_path(slug: str, code: str) -> str:
    return f"{workspace_path(slug, code)}/manifest.json"


def canonical_source_path(project_root: Path, slug: str, value: object) -> str:
    path = common.local_path(
        project_root,
        value,
        field="canonical_source_path",
        require_file=True,
    )
    prefix = f"communication/{slug}/"
    if not path.startswith(prefix):
        raise ResearchDbError(
            f"canonical_source_path 必须位于 communication/{slug}/：{path}"
        )
    remainder = path[len(prefix) :]
    if any(part.endswith("-release") for part in Path(remainder).parts[:-1]):
        raise ResearchDbError(
            "canonical communication source 不能位于 target release workspace；"
            "release 只能从共享 canonical source 构建。"
        )
    if Path(path).suffix.casefold() in COMPOSITE_OUTPUT_SUFFIXES:
        raise ResearchDbError(
            "canonical communication source 必须是可版本管理的 editable source，不能是 DOCX/XLSX/PDF/PPTX 等生成表示。"
        )
    return path


def _workspace_relative_file(
    project_root: Path,
    workspace_relative: str,
    value: object,
    *,
    field: str,
) -> str:
    raw = common.text(value, required=True, field=field)
    assert raw is not None
    relative = Path(raw)
    if relative.is_absolute():
        raise ResearchDbError(f"{field} 必须使用 target workspace 内的相对路径。")
    workspace = (project_root / workspace_relative).resolve()
    resolved = (workspace / relative).resolve()
    try:
        resolved.relative_to(workspace)
    except ValueError as exc:
        raise ResearchDbError(f"{field} 不能越出 target workspace：{raw}") from exc
    if not resolved.is_file():
        raise ResearchDbError(f"{field} 指向的文件不存在：{resolved.relative_to(project_root).as_posix()}")
    return resolved.relative_to(project_root).as_posix()


def file_content_oid(project_root: Path, relative_path: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(project_root), "hash-object", "--", relative_path],
        text=True,
        capture_output=True,
        check=False,
    )
    oid = result.stdout.strip()
    if result.returncode != 0 or not oid:
        raise ResearchDbError(f"无法计算 target source Git content OID：{relative_path}")
    return oid


def load_target_manifest(
    project_root: Path,
    *,
    slug: str,
    code: str,
    expected_canonical_source: str,
    expected_source_commit: str,
) -> dict[str, Any]:
    workspace_relative = workspace_path(slug, code)
    manifest_relative = manifest_path(slug, code)
    path = project_root / manifest_relative
    if not path.is_file():
        raise ResearchDbError(f"target release manifest 不存在：{manifest_relative}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ResearchDbError(f"target release manifest 不是有效 JSON：{manifest_relative}") from exc
    if not isinstance(payload, dict):
        raise ResearchDbError("target release manifest 顶层必须是 JSON object。")

    if common.text(payload.get("journal_code"), required=True, field="manifest journal_code") != code:
        raise ResearchDbError(
            f"target release manifest journal_code 必须与登记目标一致：{code}。"
        )
    if (
        common.text(payload.get("canonical_source"), required=True, field="manifest canonical_source")
        != expected_canonical_source
    ):
        raise ResearchDbError(
            "target release manifest canonical_source 必须指向 Communication Product 的共享 canonical source。"
        )
    if common.text(payload.get("source_commit"), required=True, field="manifest source_commit") != expected_source_commit:
        raise ResearchDbError(
            "target release manifest source_commit 必须与本次 target build source commit 一致。"
        )

    config = _workspace_relative_file(
        project_root,
        workspace_relative,
        payload.get("config"),
        field="manifest config",
    )

    build_sources_raw = payload.get("build_sources")
    if not isinstance(build_sources_raw, list) or not build_sources_raw:
        raise ResearchDbError("manifest build_sources 必须是非空数组。")
    build_sources = [
        _workspace_relative_file(
            project_root,
            workspace_relative,
            item,
            field="manifest build_sources",
        )
        for item in build_sources_raw
    ]

    template_status = common.enum_value(
        payload.get("template_status"),
        TARGET_TEMPLATE_STATUSES,
        default="not_provided",
        field="manifest template_status",
    )
    templates_raw = payload.get("templates")
    if not isinstance(templates_raw, list):
        raise ResearchDbError("manifest templates 必须是数组。")
    if template_status == "provided" and not templates_raw:
        raise ResearchDbError("template_status=provided 时 templates 不能为空。")
    if template_status != "provided" and templates_raw:
        raise ResearchDbError("template_status 不是 provided 时 templates 应为空数组。")
    templates = [
        _workspace_relative_file(
            project_root,
            workspace_relative,
            item,
            field="manifest templates",
        )
        for item in templates_raw
    ]

    qa_raw = payload.get("qa_evidence")
    if not isinstance(qa_raw, list) or not qa_raw:
        raise ResearchDbError("manifest qa_evidence 必须是非空数组。")
    qa_evidence = [
        _workspace_relative_file(
            project_root,
            workspace_relative,
            item,
            field="manifest qa_evidence",
        )
        for item in qa_raw
    ]

    generated_raw = payload.get("generated_outputs")
    if not isinstance(generated_raw, list) or not generated_raw:
        raise ResearchDbError("manifest generated_outputs 必须是非空数组。")
    generated_outputs: list[str] = []
    for item in generated_raw:
        value = common.text(item, required=True, field="manifest generated_outputs")
        assert value is not None
        candidate = Path(value)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ResearchDbError("manifest generated_outputs 必须使用安全的相对目标文件名。")
        generated_outputs.append(candidate.as_posix())

    files: list[tuple[str, str]] = [("manifest", manifest_relative), ("config", config)]
    files.extend(("build_source", item) for item in build_sources)
    files.extend(("template", item) for item in templates)
    files.extend(("qa_evidence", item) for item in qa_evidence)
    if len({path for _, path in files}) != len(files):
        raise ResearchDbError("target release manifest 不得把同一个文件登记为多个职责。")

    return {
        "workspace_path": workspace_relative,
        "manifest_path": manifest_relative,
        "template_status": template_status,
        "generated_outputs": generated_outputs,
        "files": files,
    }


def stored_generated_outputs(
    project_root: Path,
    workspace_relative: str,
    generated_outputs: list[str] | None = None,
) -> list[str]:
    workspace = project_root / workspace_relative
    if not workspace.is_dir():
        return []
    found = {
        path.relative_to(project_root).as_posix()
        for path in workspace.rglob("*")
        if path.is_file() and path.suffix.casefold() in COMPOSITE_OUTPUT_SUFFIXES
    }
    for output in generated_outputs or []:
        candidate = (workspace / output).resolve()
        try:
            candidate.relative_to(workspace.resolve())
        except ValueError:
            continue
        if candidate.is_file():
            found.add(candidate.relative_to(project_root).as_posix())
    return sorted(found)

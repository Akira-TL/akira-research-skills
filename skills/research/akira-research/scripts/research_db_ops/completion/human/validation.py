from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote


_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
_H1_RE = re.compile(r"(?m)^#\s+(.+?)\s*$")
_H2_RE = re.compile(r"(?m)^##\s+(.+?)\s*$")
_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_VERSIONED_MARKER_RE = re.compile(r"<!--\s*akira:[^>\s]+:v\d+(?:\.\d+)*\s*-->", re.IGNORECASE)


def _sections(text: str) -> tuple[list[str], dict[str, str]]:
    headings = list(_H2_RE.finditer(text))
    order: list[str] = []
    sections: dict[str, str] = {}
    for index, match in enumerate(headings):
        name = match.group(1).strip()
        order.append(name)
        start = match.end()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        sections[name] = text[start:end].strip()
    return order, sections


def _markdown_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    elif " " in target:
        target = target.split(" ", 1)[0]
    return unquote(target.strip())


def human_markdown_blockers(
    project_root: Path,
    relative_path: str,
    *,
    expected_h1: str,
    expected_h2: tuple[str, ...],
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    path = project_root / relative_path
    text = path.read_text(encoding="utf-8", errors="ignore")
    blockers: list[dict[str, Any]] = []

    versioned_markers = [match.group(0) for match in _VERSIONED_MARKER_RE.finditer(text)]
    if versioned_markers:
        blockers.append(
            {
                "reason": "human_markdown_versioned_marker",
                "path": relative_path,
                "markers": versioned_markers,
            }
        )

    h1 = [match.group(1).strip() for match in _H1_RE.finditer(text)]
    if h1 != [expected_h1]:
        blockers.append(
            {
                "reason": "human_markdown_h1_invalid",
                "path": relative_path,
                "expected": expected_h1,
                "headings": h1,
                "count": len(h1),
            }
        )

    order, sections = _sections(text)
    if tuple(order) != expected_h2:
        blockers.append(
            {
                "reason": "human_markdown_section_order_invalid",
                "path": relative_path,
                "expected": list(expected_h2),
                "actual": order,
            }
        )

    empty = [name for name in expected_h2 if name in sections and not sections[name].strip()]
    if empty:
        blockers.append(
            {
                "reason": "human_markdown_empty_sections",
                "path": relative_path,
                "sections": empty,
            }
        )

    root = project_root.resolve()
    for match in _LINK_RE.finditer(text):
        target = _markdown_target(match.group(1))
        if not target or target.startswith("#"):
            continue
        if target.casefold().startswith("file:"):
            blockers.append(
                {
                    "reason": "human_markdown_link_absolute",
                    "path": relative_path,
                    "target": target,
                }
            )
            continue
        if _SCHEME_RE.match(target):
            continue
        path_part = target.split("#", 1)[0].split("?", 1)[0]
        if not path_part:
            continue
        if Path(path_part).is_absolute():
            blockers.append(
                {
                    "reason": "human_markdown_link_absolute",
                    "path": relative_path,
                    "target": target,
                }
            )
            continue
        resolved = (path.parent / path_part).resolve()
        try:
            resolved_relative = resolved.relative_to(root).as_posix()
        except ValueError:
            blockers.append(
                {
                    "reason": "human_markdown_link_outside_project",
                    "path": relative_path,
                    "target": target,
                }
            )
            continue
        if resolved_relative == ".research" or resolved_relative.startswith(".research/"):
            blockers.append(
                {
                    "reason": "human_markdown_link_internal",
                    "path": relative_path,
                    "target": target,
                }
            )
            continue
        if not resolved.exists():
            blockers.append(
                {
                    "reason": "human_markdown_link_missing",
                    "path": relative_path,
                    "target": target,
                }
            )

    return sections, blockers

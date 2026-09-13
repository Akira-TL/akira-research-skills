from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path
from typing import Any

from .research_tree import get_research_tree


VIEW_PATH = "research-tree/README.md"


def _mermaid_text(value: object) -> str:
    return (
        str(value or "")
        .replace("\\", "\\\\")
        .replace('"', "'")
        .replace("\n", " ")
        .strip()
    )


def _node_declaration(node: dict[str, Any]) -> str:
    node_id = int(node["id"])
    label = _mermaid_text(node["label"])
    kind = _mermaid_text(node["kind"])
    status = _mermaid_text(node["workflow_status"])
    return f'N{node_id}["{label}<br/>{kind} · {status}"]'


def _relative_artifact_link(view_path: Path, artifact_path: str) -> str:
    return Path(os.path.relpath(artifact_path, start=view_path.parent.as_posix())).as_posix()


def render_research_tree_view(project_root: Path) -> dict[str, Any]:
    tree = get_research_tree(project_root, limit=None)
    nodes = list(tree["nodes"])
    edges = list(tree["edges"])
    view_path = Path(VIEW_PATH)
    output = project_root / view_path
    output.parent.mkdir(parents=True, exist_ok=True)

    grouped: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    grouped_node_ids: set[int] = set()
    for node in nodes:
        if node["parent_node_id"] is None:
            continue
        grouped[(int(node["parent_node_id"]), str(node["kind"]))].append(node)
    visual_groups = [
        (key, sorted(items, key=lambda item: int(item["id"])))
        for key, items in sorted(grouped.items(), key=lambda item: (item[0][0], item[0][1]))
        if len(items) >= 2
    ]
    for _, items in visual_groups:
        grouped_node_ids.update(int(item["id"]) for item in items)

    lines = [
        "# Research Tree",
        "",
        "## Graph",
        "",
        "```mermaid",
        "flowchart TD",
    ]

    for node in sorted(nodes, key=lambda item: int(item["id"])):
        if int(node["id"]) not in grouped_node_ids:
            lines.append("    " + _node_declaration(node))

    for (parent_id, kind), items in visual_groups:
        group_id = f"G{parent_id}_{kind}"
        group_label = _mermaid_text(f"{kind} siblings")
        lines.extend(
            [
                f'    subgraph {group_id}["{group_label}"]',
                "        direction TB",
            ]
        )
        for node in items:
            lines.append("        " + _node_declaration(node))
        lines.append("    end")

    for node in sorted(nodes, key=lambda item: int(item["id"])):
        if node["parent_node_id"] is not None:
            lines.append(f"    N{int(node['parent_node_id'])} --> N{int(node['id'])}")

    for edge in sorted(edges, key=lambda item: int(item["id"])):
        relation = _mermaid_text(edge["relation"])
        lines.append(
            f"    N{int(edge['source_node_id'])} -. {relation} .-> N{int(edge['target_node_id'])}"
        )

    lines.extend(["```", "", "## Node Index", ""])
    if not nodes:
        lines.append("不适用：当前 Research Tree 尚无科研节点。")
    else:
        lines.extend(
            [
                "| Node | 类型 | 状态 | 科研对象 | 人类入口 |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for node in sorted(nodes, key=lambda item: int(item["id"])):
            artifact = str(node["artifact_path"] or "").strip()
            link = (
                f"[打开]({_relative_artifact_link(view_path, artifact)})"
                if artifact
                else "—"
            )
            label = str(node["label"]).replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| N{int(node['id'])} | {node['kind']} | {node['workflow_status']} | {label} | {link} |"
            )

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "path": view_path.as_posix(),
        "node_count": len(nodes),
        "edge_count": len(edges),
    }

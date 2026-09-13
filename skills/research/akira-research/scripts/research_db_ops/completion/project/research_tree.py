from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

from research_db_ops.project.research_tree_view import VIEW_PATH
from research_db_support.storage import connect, database_path

from ..human import human_markdown_blockers


def _git(project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(project_root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def _commit_exists(project_root: Path, ref: str) -> bool:
    return _git(project_root, "rev-parse", "--verify", f"{ref}^{{commit}}").returncode == 0


def _is_ancestor(project_root: Path, ancestor: str, descendant: str) -> bool:
    return _git(project_root, "merge-base", "--is-ancestor", ancestor, descendant).returncode == 0


def _changed_paths(project_root: Path, start: str, end: str) -> set[str]:
    result = _git(project_root, "diff", "--name-only", f"{start}..{end}")
    if result.returncode != 0:
        return set()
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _only_provenance_changes(project_root: Path, start: str, end: str) -> bool:
    if start == end:
        return True
    if not _is_ancestor(project_root, start, end):
        return False
    return _changed_paths(project_root, start, end) <= {".research/research.sqlite"}


def _is_annotated_tag(project_root: Path, tag: str) -> bool:
    result = _git(project_root, "cat-file", "-t", f"refs/tags/{tag}")
    return result.returncode == 0 and result.stdout.strip() == "tag"


def _merge_parents(project_root: Path, commit: str) -> list[str]:
    result = _git(project_root, "rev-list", "--parents", "-n", "1", commit)
    if result.returncode != 0:
        return []
    return result.stdout.split()[1:]


def _is_merge_commit(project_root: Path, commit: str) -> bool:
    return len(_merge_parents(project_root, commit)) >= 2


def _research_tree_view_edges(text: str) -> tuple[set[int], set[tuple[int, int]], set[tuple[int, str, int]]]:
    node_ids = {
        int(match.group(1))
        for match in re.finditer(r"(?m)^\s*N(\d+)[\[\{(]", text)
    }
    parent_edges = {
        (int(match.group(1)), int(match.group(2)))
        for match in re.finditer(r"(?m)^\s*N(\d+)\s*-->\s*N(\d+)\s*$", text)
    }
    semantic_edges = {
        (int(match.group(1)), match.group(2), int(match.group(3)))
        for match in re.finditer(
            r"(?m)^\s*N(\d+)\s*-\.\s*([A-Za-z_][A-Za-z0-9_]*)\s*\.->\s*N(\d+)\s*$",
            text,
        )
    }
    return node_ids, parent_edges, semantic_edges


def research_tree_completion_readiness(project_root: Path) -> dict[str, Any]:
    db_path = database_path(project_root)
    if not db_path.exists():
        return {
            "ready": False,
            "checked": True,
            "blockers": [{"reason": "database_missing"}],
            "node_count": 0,
            "edge_count": 0,
            "state_present": False,
        }

    blockers: list[dict[str, Any]] = []
    with connect(db_path) as connection:
        tables = {
            str(row["name"])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        required = {"research_nodes", "research_edges", "research_tree_state", "research_git_branches"}
        missing = sorted(required - tables)
        if missing:
            return {
                "ready": False,
                "checked": True,
                "blockers": [{"reason": "research_tree_schema_missing", "tables": missing}],
                "node_count": 0,
                "edge_count": 0,
                "state_present": False,
            }

        node_rows = list(connection.execute("SELECT id, parent_node_id FROM research_nodes ORDER BY id"))
        node_count = len(node_rows)
        expected_node_ids = {int(row["id"]) for row in node_rows}
        expected_parent_edges = {
            (int(row["parent_node_id"]), int(row["id"]))
            for row in node_rows
            if row["parent_node_id"] is not None
        }
        semantic_rows = list(
            connection.execute(
                "SELECT source_node_id, relation, target_node_id FROM research_edges ORDER BY id"
            )
        )
        edge_count = len(semantic_rows)
        expected_semantic_edges = {
            (int(row["source_node_id"]), str(row["relation"]), int(row["target_node_id"]))
            for row in semantic_rows
        }
        state = connection.execute(
            """
            SELECT st.root_node_id, st.active_node_id,
                   r.slug AS root_slug, r.parent_node_id AS root_parent_id,
                   a.slug AS active_slug, a.workflow_status AS active_status
            FROM research_tree_state st
            LEFT JOIN research_nodes r ON r.id = st.root_node_id
            LEFT JOIN research_nodes a ON a.id = st.active_node_id
            WHERE st.id = 1
            """
        ).fetchone()
        state_present = state is not None

        if node_count == 0:
            if state_present:
                blockers.append({"reason": "research_tree_state_without_nodes"})
        elif not state_present:
            blockers.append({"reason": "research_tree_state_missing"})
        else:
            if state["root_slug"] is None or state["active_slug"] is None:
                blockers.append({"reason": "research_tree_state_dangling"})
            else:
                if state["root_parent_id"] is not None:
                    blockers.append(
                        {
                            "reason": "research_tree_root_has_parent",
                            "root": state["root_slug"],
                        }
                    )
                seen: set[int] = set()
                current_id: int | None = int(state["active_node_id"])
                reached_root = False
                while current_id is not None:
                    if current_id in seen:
                        blockers.append({"reason": "research_tree_parent_cycle"})
                        break
                    seen.add(current_id)
                    row = connection.execute(
                        "SELECT id, parent_node_id FROM research_nodes WHERE id = ?",
                        (current_id,),
                    ).fetchone()
                    if row is None:
                        blockers.append({"reason": "research_tree_parent_chain_dangling"})
                        break
                    if int(row["id"]) == int(state["root_node_id"]):
                        reached_root = True
                        break
                    current_id = (
                        int(row["parent_node_id"])
                        if row["parent_node_id"] is not None
                        else None
                    )
                if not reached_root:
                    blockers.append(
                        {
                            "reason": "research_tree_active_outside_root",
                            "root": state["root_slug"],
                            "active": state["active_slug"],
                        }
                    )

        workflow_started = connection.execute(
            "SELECT value FROM meta WHERE key = 'research_git_workflow_started_at'"
        ).fetchone()
        if workflow_started is not None:
            for node in connection.execute(
                """
                SELECT slug, kind, workflow_status, closure_reason, updated_at
                FROM research_nodes
                WHERE workflow_status = 'closed' AND updated_at >= ?
                ORDER BY id
                """,
                (str(workflow_started["value"]),),
            ):
                if not node["closure_reason"] or not str(node["closure_reason"]).strip():
                    blockers.append(
                        {
                            "reason": "research_tree_closed_without_reason",
                            "node": node["slug"],
                        }
                    )

        for branch in connection.execute(
            """
            SELECT b.*, n.slug AS node_slug, n.kind AS node_kind
            FROM research_git_branches b
            JOIN research_nodes n ON n.id = b.node_id
            ORDER BY b.id
            """
        ):
            expected = f"research/{branch['node_kind']}/{branch['node_slug']}"
            if str(branch["branch_name"]) != expected:
                blockers.append(
                    {
                        "reason": "research_git_branch_name_invalid",
                        "node": branch["node_slug"],
                        "branch": branch["branch_name"],
                        "expected": expected,
                    }
                )
            base_commit = str(branch["base_commit"])
            tip_commit = str(branch["tip_commit"])
            if not _commit_exists(project_root, base_commit) or not _commit_exists(project_root, tip_commit):
                blockers.append(
                    {
                        "reason": "research_git_commit_missing",
                        "node": branch["node_slug"],
                        "base_commit": base_commit,
                        "tip_commit": tip_commit,
                    }
                )
                continue
            if not _is_ancestor(project_root, base_commit, tip_commit):
                blockers.append(
                    {
                        "reason": "research_git_base_not_ancestor",
                        "node": branch["node_slug"],
                    }
                )
            disposition = str(branch["disposition"])
            if disposition == "active":
                ref = f"refs/heads/{branch['branch_name']}"
                current = _git(project_root, "rev-parse", "--verify", ref)
                current_commit = current.stdout.strip() if current.returncode == 0 else ""
                if not current_commit or not _only_provenance_changes(project_root, tip_commit, current_commit):
                    blockers.append(
                        {
                            "reason": "research_git_active_branch_out_of_sync",
                            "node": branch["node_slug"],
                            "branch": branch["branch_name"],
                        }
                    )
            elif disposition == "merged":
                final_ref = str(branch["final_ref"] or "")
                merge_parents = _merge_parents(project_root, final_ref) if final_ref else []
                if (
                    not final_ref
                    or not _commit_exists(project_root, final_ref)
                    or len(merge_parents) < 2
                    or merge_parents[0] != base_commit
                    or not _is_ancestor(project_root, tip_commit, final_ref)
                    or not _is_ancestor(project_root, final_ref, "main")
                ):
                    blockers.append(
                        {
                            "reason": "research_git_merged_tip_not_in_main",
                            "node": branch["node_slug"],
                            "final_ref": final_ref,
                        }
                    )
            elif disposition == "archived":
                expected_tag = f"research-closed/{branch['node_kind']}/{branch['node_slug']}"
                if str(branch["final_ref"]) != expected_tag:
                    blockers.append(
                        {
                            "reason": "research_git_archive_ref_invalid",
                            "node": branch["node_slug"],
                            "expected": expected_tag,
                        }
                    )
                tag_commit = _git(project_root, "rev-parse", "--verify", f"{expected_tag}^{{commit}}")
                archived_commit = tag_commit.stdout.strip() if tag_commit.returncode == 0 else ""
                if (
                    not archived_commit
                    or not _is_annotated_tag(project_root, expected_tag)
                    or not _only_provenance_changes(project_root, tip_commit, archived_commit)
                ):
                    blockers.append(
                        {
                            "reason": "research_git_archive_tag_mismatch",
                            "node": branch["node_slug"],
                            "tag": expected_tag,
                        }
                    )

    if node_count:
        view_path = project_root / VIEW_PATH
        if not view_path.exists():
            blockers.append({"reason": "research_tree_view_missing", "path": VIEW_PATH})
        else:
            _, format_blockers = human_markdown_blockers(
                project_root,
                VIEW_PATH,
                expected_h1="Research Tree",
                expected_h2=("Graph", "Node Index"),
            )
            blockers.extend(format_blockers)
            text = view_path.read_text(encoding="utf-8", errors="ignore")
            mermaid_blocks = re.findall(r"```mermaid\s*\n(.*?)```", text, flags=re.DOTALL)
            if len(mermaid_blocks) != 1:
                blockers.append(
                    {
                        "reason": "research_tree_view_mermaid_block_invalid",
                        "count": len(mermaid_blocks),
                    }
                )
            graph_text = mermaid_blocks[0] if mermaid_blocks else ""
            actual_node_ids, actual_parent_edges, actual_semantic_edges = _research_tree_view_edges(
                graph_text
            )
            missing_nodes = sorted(expected_node_ids - actual_node_ids)
            extra_nodes = sorted(actual_node_ids - expected_node_ids)
            if missing_nodes:
                blockers.append(
                    {
                        "reason": "research_tree_view_missing_node",
                        "nodes": missing_nodes,
                    }
                )
            if extra_nodes:
                blockers.append(
                    {
                        "reason": "research_tree_view_extra_node",
                        "nodes": extra_nodes,
                    }
                )

            missing_parent = sorted(expected_parent_edges - actual_parent_edges)
            missing_semantic = sorted(expected_semantic_edges - actual_semantic_edges)
            if missing_parent or missing_semantic:
                blockers.append(
                    {
                        "reason": "research_tree_view_missing_edge",
                        "parent_edges": missing_parent,
                        "semantic_edges": missing_semantic,
                    }
                )

            extra_parent = sorted(actual_parent_edges - expected_parent_edges)
            extra_semantic = sorted(actual_semantic_edges - expected_semantic_edges)
            if extra_parent or extra_semantic:
                blockers.append(
                    {
                        "reason": "research_tree_view_extra_edge",
                        "parent_edges": extra_parent,
                        "semantic_edges": extra_semantic,
                    }
                )

    return {
        "ready": not blockers,
        "checked": True,
        "blockers": blockers,
        "node_count": node_count,
        "edge_count": edge_count,
        "state_present": state_present,
    }

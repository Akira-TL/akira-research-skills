from __future__ import annotations

from pathlib import Path
from typing import Any

from research_db_support.storage import connect, database_path
from ..git import commit_has_path, run_git
from ..language import canonical_paths


HUMAN_COMMUNICATION_ROOT = "communication"
INTERNAL_COMMUNICATION_ROOT = ".research/communication"


def _workspace_files(project_root: Path) -> tuple[set[str], list[dict[str, Any]]]:
    actual_paths: set[str] = set()
    blockers: list[dict[str, Any]] = []

    human_root = project_root / HUMAN_COMMUNICATION_ROOT
    if human_root.exists():
        for child in sorted(human_root.iterdir(), key=lambda path: path.name.casefold()):
            relative = child.relative_to(project_root).as_posix()
            if child.is_file():
                if child.name == "README.md":
                    continue
                actual_paths.add(relative)
                blockers.append(
                    {
                        "reason": "communication_human_view_unexpected_top_level",
                        "path": relative,
                    }
                )
                continue
            if child.is_dir():
                actual_paths.update(
                    path.relative_to(project_root).as_posix()
                    for path in child.rglob("*")
                    if path.is_file()
                )

    internal_root = project_root / INTERNAL_COMMUNICATION_ROOT
    if internal_root.exists():
        for child in sorted(internal_root.iterdir(), key=lambda path: path.name.casefold()):
            relative = child.relative_to(project_root).as_posix()
            if child.is_file():
                actual_paths.add(relative)
                blockers.append(
                    {
                        "reason": "communication_internal_support_unexpected_top_level",
                        "path": relative,
                    }
                )
                continue
            if child.is_dir():
                actual_paths.update(
                    path.relative_to(project_root).as_posix()
                    for path in child.rglob("*")
                    if path.is_file()
                )

    return actual_paths, blockers


def _artifact_matches_product_workspace(path: str, slug: str) -> bool:
    return path.startswith(f"{HUMAN_COMMUNICATION_ROOT}/{slug}/") or path.startswith(
        f"{INTERNAL_COMMUNICATION_ROOT}/{slug}/"
    )


def communication_completion_readiness(project_root: Path) -> dict[str, Any]:
    actual_paths, blockers = _workspace_files(project_root)
    has_assets = bool(actual_paths)
    db_path = database_path(project_root)
    if not db_path.exists():
        return {
            "ready": not has_assets and not blockers,
            "blockers": (
                blockers + [{"reason": "communication_assets_present_without_database"}]
                if has_assets
                else blockers
            ),
            "product_count": 0,
            "completed_product_count": 0,
        }

    with connect(db_path) as connection:
        tables = {
            str(row["name"])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        required = {"communication_products", "communication_artifacts"}
        missing = sorted(required - tables)
        if missing:
            return {
                "ready": not has_assets and not blockers,
                "blockers": (
                    blockers + [{"reason": "communication_schema_missing", "tables": missing}]
                    if has_assets
                    else blockers
                ),
                "product_count": 0,
                "completed_product_count": 0,
            }

        product_count = int(connection.execute("SELECT COUNT(*) FROM communication_products").fetchone()[0])
        completed_product_count = int(
            connection.execute("SELECT COUNT(*) FROM communication_products WHERE status = 'completed'").fetchone()[0]
        )
        artifact_rows = connection.execute(
            """
            SELECT ca.*, cp.slug AS product_slug
            FROM communication_artifacts AS ca
            JOIN communication_products AS cp ON cp.id = ca.product_id
            ORDER BY ca.id
            """
        ).fetchall()
        registered_paths = {str(row["path"]) for row in artifact_rows}
        orphaned = sorted(actual_paths - registered_paths)
        if orphaned:
            blockers.append({"reason": "communication_artifacts_unregistered", "paths": orphaned})
        if has_assets and product_count == 0:
            blockers.append({"reason": "communication_assets_present_without_product_record"})

        for artifact in artifact_rows:
            path = str(artifact["path"])
            slug = str(artifact["product_slug"])
            in_communication_workspace = path.startswith(
                f"{HUMAN_COMMUNICATION_ROOT}/"
            ) or path.startswith(f"{INTERNAL_COMMUNICATION_ROOT}/")
            if in_communication_workspace and not _artifact_matches_product_workspace(path, slug):
                blockers.append(
                    {
                        "reason": "communication_artifact_product_mismatch",
                        "communication": slug,
                        "path": path,
                    }
                )
            if (
                artifact["timing_role"] == "derived_output"
                and artifact["role"] != "generator"
                and not _artifact_matches_product_workspace(path, slug)
            ):
                blockers.append(
                    {
                        "reason": "communication_derived_output_outside_workspace",
                        "communication": slug,
                        "path": path,
                    }
                )

        derived_communication_paths = {
            str(row["path"])
            for row in artifact_rows
            if row["timing_role"] == "derived_output"
        }
        scientific_paths = [
            path
            for path in canonical_paths(project_root)
            if path not in {"RESEARCH.md", ".research/research.sqlite"}
            and not path.startswith(f"{HUMAN_COMMUNICATION_ROOT}/")
            and not path.startswith(f"{INTERNAL_COMMUNICATION_ROOT}/")
            and path not in derived_communication_paths
        ]
        for product in connection.execute(
            "SELECT * FROM communication_products WHERE status = 'completed' ORDER BY id"
        ):
            product_id = int(product["id"])
            slug = str(product["slug"])
            source_commit = str(product["source_commit"] or "").strip()
            artifacts = connection.execute(
                "SELECT * FROM communication_artifacts WHERE product_id = ? ORDER BY id",
                (product_id,),
            ).fetchall()
            if not artifacts:
                blockers.append({"reason": "completed_communication_missing_artifacts", "communication": slug})
                continue
            if not source_commit:
                blockers.append({"reason": "communication_source_commit_missing", "communication": slug})
                continue
            if run_git(project_root, "cat-file", "-e", f"{source_commit}^{{commit}}").returncode != 0:
                blockers.append(
                    {
                        "reason": "communication_source_commit_not_found",
                        "communication": slug,
                        "source_commit": source_commit,
                    }
                )
                continue
            if run_git(project_root, "merge-base", "--is-ancestor", source_commit, "HEAD").returncode != 0:
                blockers.append(
                    {
                        "reason": "communication_source_commit_not_ancestor",
                        "communication": slug,
                        "source_commit": source_commit,
                    }
                )
                continue

            wrong_timing: list[str] = []
            for artifact in artifacts:
                path = str(artifact["path"])
                existed = commit_has_path(project_root, source_commit, path)
                if artifact["timing_role"] == "derived_output" and existed:
                    wrong_timing.append(path)
                if artifact["timing_role"] == "source_support" and not existed:
                    wrong_timing.append(path)
            if wrong_timing:
                blockers.append(
                    {
                        "reason": "communication_artifact_timing_mismatch",
                        "communication": slug,
                        "source_commit": source_commit,
                        "paths": sorted(wrong_timing),
                    }
                )

            changed_science = [
                path
                for path in scientific_paths
                if run_git(project_root, "diff", "--quiet", source_commit, "HEAD", "--", path).returncode != 0
            ]
            if changed_science:
                blockers.append(
                    {
                        "reason": "scientific_source_changed_after_communication_freeze",
                        "communication": slug,
                        "source_commit": source_commit,
                        "paths": changed_science,
                    }
                )

    return {
        "ready": not blockers,
        "blockers": blockers,
        "product_count": product_count,
        "completed_product_count": completed_product_count,
    }

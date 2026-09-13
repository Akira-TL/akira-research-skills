from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

from research_db_support.storage import ResearchDbError, connect, database_path
from research_db_ops.communication.release_tag import (
    BASELINE_APPROVAL_SOURCES,
    RELEASE_EVIDENCE_SOURCES,
    parse_communication_tag,
)
from research_db_ops.communication.target import (
    file_content_oid,
    load_target_manifest,
    manifest_path,
    stored_generated_outputs,
    workspace_path,
)
from ..git import commit_has_path, run_git
from ..human import human_navigation_index_paths
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


def _target_release_directories(project_root: Path) -> set[str]:
    human_root = project_root / HUMAN_COMMUNICATION_ROOT
    targets: set[str] = set()
    if not human_root.is_dir():
        return targets
    for product_dir in human_root.iterdir():
        if not product_dir.is_dir():
            continue
        for child in product_dir.iterdir():
            if child.is_dir() and child.name.endswith("-release"):
                targets.add(child.relative_to(project_root).as_posix())
    return targets


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
        required = {
            "communication_products",
            "communication_artifacts",
            "communication_journals",
            "communication_target_workspaces",
            "communication_target_files",
            "communication_release_tags",
        }
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
        target_rows = connection.execute(
            """
            SELECT ctw.*, cp.slug AS product_slug,
                   cp.canonical_source_path AS canonical_source_path,
                   cj.name AS journal_name
            FROM communication_target_workspaces AS ctw
            JOIN communication_products AS cp ON cp.id = ctw.product_id
            JOIN communication_journals AS cj ON cj.code = ctw.journal_code
            ORDER BY ctw.id
            """
        ).fetchall()
        target_file_rows = connection.execute(
            """
            SELECT ctf.*, ctw.product_id AS product_id
            FROM communication_target_files AS ctf
            JOIN communication_target_workspaces AS ctw ON ctw.id = ctf.target_id
            ORDER BY ctf.id
            """
        ).fetchall()
        release_tag_rows = connection.execute(
            """
            SELECT crt.*, ctw.product_id AS product_id, ctw.journal_code AS journal_code,
                   cp.slug AS product_slug
            FROM communication_release_tags AS crt
            JOIN communication_target_workspaces AS ctw ON ctw.id = crt.target_id
            JOIN communication_products AS cp ON cp.id = ctw.product_id
            ORDER BY crt.id
            """
        ).fetchall()
        actual_target_directories = _target_release_directories(project_root)
        registered_target_directories = {
            str(row["workspace_path"]) for row in target_rows
        }
        unregistered_target_directories = sorted(
            actual_target_directories - registered_target_directories
        )
        if unregistered_target_directories:
            blockers.append(
                {
                    "reason": "communication_target_workspace_unregistered",
                    "paths": unregistered_target_directories,
                }
            )
        registered_paths = {str(row["path"]) for row in artifact_rows}
        registered_paths.update(str(row["path"]) for row in target_file_rows)
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

        artifact_paths_by_product: dict[int, set[str]] = {}
        for artifact in artifact_rows:
            artifact_paths_by_product.setdefault(int(artifact["product_id"]), set()).add(
                str(artifact["path"])
            )
        target_files_by_target: dict[int, list[Any]] = {}
        for target_file in target_file_rows:
            target_files_by_target.setdefault(int(target_file["target_id"]), []).append(target_file)

        for target in target_rows:
            target_id = int(target["id"])
            product_id = int(target["product_id"])
            slug = str(target["product_slug"])
            code = str(target["journal_code"])
            canonical_source = str(target["canonical_source_path"] or "").strip()
            source_commit = str(target["source_commit"] or "").strip()
            expected_workspace = workspace_path(slug, code)
            expected_manifest = manifest_path(slug, code)

            if str(target["workspace_path"]) != expected_workspace:
                blockers.append(
                    {
                        "reason": "communication_target_workspace_identity_mismatch",
                        "communication": slug,
                        "journal_code": code,
                        "path": str(target["workspace_path"]),
                        "expected": expected_workspace,
                    }
                )
            if str(target["manifest_path"]) != expected_manifest:
                blockers.append(
                    {
                        "reason": "communication_target_manifest_identity_mismatch",
                        "communication": slug,
                        "journal_code": code,
                        "path": str(target["manifest_path"]),
                        "expected": expected_manifest,
                    }
                )
            if not canonical_source:
                blockers.append(
                    {
                        "reason": "communication_target_canonical_source_missing",
                        "communication": slug,
                        "journal_code": code,
                    }
                )
                continue
            if canonical_source not in artifact_paths_by_product.get(product_id, set()):
                blockers.append(
                    {
                        "reason": "communication_canonical_source_unregistered",
                        "communication": slug,
                        "path": canonical_source,
                    }
                )
            source_remainder = canonical_source.removeprefix(f"communication/{slug}/")
            if (
                not canonical_source.startswith(f"communication/{slug}/")
                or any(part.endswith("-release") for part in Path(source_remainder).parts[:-1])
            ):
                blockers.append(
                    {
                        "reason": "communication_canonical_source_inside_target",
                        "communication": slug,
                        "path": canonical_source,
                    }
                )

            if not source_commit:
                blockers.append(
                    {
                        "reason": "communication_target_source_commit_missing",
                        "communication": slug,
                        "journal_code": code,
                    }
                )
            elif run_git(
                project_root, "cat-file", "-e", f"{source_commit}^{{commit}}"
            ).returncode != 0:
                blockers.append(
                    {
                        "reason": "communication_target_source_commit_not_found",
                        "communication": slug,
                        "journal_code": code,
                        "source_commit": source_commit,
                    }
                )
            elif run_git(
                project_root, "merge-base", "--is-ancestor", source_commit, "HEAD"
            ).returncode != 0:
                blockers.append(
                    {
                        "reason": "communication_target_source_commit_not_ancestor",
                        "communication": slug,
                        "journal_code": code,
                        "source_commit": source_commit,
                    }
                )
            elif not commit_has_path(project_root, source_commit, canonical_source):
                blockers.append(
                    {
                        "reason": "communication_target_source_missing_at_commit",
                        "communication": slug,
                        "journal_code": code,
                        "source_commit": source_commit,
                        "path": canonical_source,
                    }
                )
            elif run_git(
                project_root,
                "diff",
                "--quiet",
                source_commit,
                "HEAD",
                "--",
                canonical_source,
            ).returncode != 0:
                blockers.append(
                    {
                        "reason": "communication_target_source_drift",
                        "communication": slug,
                        "journal_code": code,
                        "source_commit": source_commit,
                        "path": canonical_source,
                    }
                )

            try:
                manifest = load_target_manifest(
                    project_root,
                    slug=slug,
                    code=code,
                    expected_canonical_source=canonical_source,
                    expected_source_commit=source_commit,
                )
            except ResearchDbError as exc:
                blockers.append(
                    {
                        "reason": "communication_target_manifest_invalid",
                        "communication": slug,
                        "journal_code": code,
                        "detail": str(exc),
                    }
                )
                manifest = None

            recorded_target_files = target_files_by_target.get(target_id, [])
            recorded_paths = {str(row["path"]) for row in recorded_target_files}
            if manifest is not None:
                declared_paths = {path for _, path in manifest["files"]}
                if recorded_paths != declared_paths:
                    blockers.append(
                        {
                            "reason": "communication_target_manifest_file_drift",
                            "communication": slug,
                            "journal_code": code,
                            "recorded": sorted(recorded_paths),
                            "declared": sorted(declared_paths),
                        }
                    )

            for target_file in recorded_target_files:
                path = str(target_file["path"])
                file_path = project_root / path
                if not file_path.is_file():
                    blockers.append(
                        {
                            "reason": "communication_target_file_missing",
                            "communication": slug,
                            "journal_code": code,
                            "path": path,
                        }
                    )
                    continue
                try:
                    current_oid = file_content_oid(project_root, path)
                except ResearchDbError as exc:
                    blockers.append(
                        {
                            "reason": "communication_target_file_oid_unavailable",
                            "communication": slug,
                            "journal_code": code,
                            "path": path,
                            "detail": str(exc),
                        }
                    )
                    continue
                if current_oid != str(target_file["content_oid"]):
                    blockers.append(
                        {
                            "reason": "communication_target_build_source_drift",
                            "communication": slug,
                            "journal_code": code,
                            "path": path,
                        }
                    )

            declared_generated_outputs = (
                list(manifest["generated_outputs"]) if manifest is not None else None
            )
            stored_outputs = stored_generated_outputs(
                project_root,
                expected_workspace,
                declared_generated_outputs,
            )
            if stored_outputs:
                blockers.append(
                    {
                        "reason": "communication_target_generated_output_stored",
                        "communication": slug,
                        "journal_code": code,
                        "paths": stored_outputs,
                    }
                )

            workspace_root = project_root / expected_workspace
            if workspace_root.is_dir():
                actual_target_paths = {
                    path.relative_to(project_root).as_posix()
                    for path in workspace_root.rglob("*")
                    if path.is_file()
                }
                allowed_target_paths = recorded_paths | set(stored_outputs)
                unexpected_target_paths = sorted(
                    actual_target_paths - allowed_target_paths
                )
                if unexpected_target_paths:
                    blockers.append(
                        {
                            "reason": "communication_target_unexpected_file",
                            "communication": slug,
                            "journal_code": code,
                            "paths": unexpected_target_paths,
                        }
                    )

        checkpoint_rows_by_target: dict[int, list[Any]] = {}
        for row in release_tag_rows:
            if str(row["tag_kind"]) == "checkpoint":
                checkpoint_rows_by_target.setdefault(int(row["target_id"]), []).append(row)
        for target_id, rows in checkpoint_rows_by_target.items():
            ordered = sorted(
                rows,
                key=lambda row: (int(row["version_number"]), int(row["revision_number"])),
            )
            previous: tuple[int, int] | None = None
            for row in ordered:
                current = (int(row["version_number"]), int(row["revision_number"]))
                slug = str(row["product_slug"])
                code = str(row["journal_code"])
                if previous is None:
                    if current != (1, 0):
                        blockers.append(
                            {
                                "reason": "communication_release_version_sequence_invalid",
                                "communication": slug,
                                "journal_code": code,
                                "version": f"{current[0]}.{current[1]}",
                                "detail": "lineage 必须从 1.0 开始。",
                            }
                        )
                elif current[0] == previous[0] and current[1] == previous[1] + 1:
                    pass
                elif current[0] == previous[0] + 1 and current[1] == 0:
                    approval_source = str(row["baseline_approval_source"] or "").strip()
                    approval = str(row["baseline_approval"] or "").strip()
                    if approval_source not in BASELINE_APPROVAL_SOURCES or not approval:
                        blockers.append(
                            {
                                "reason": "communication_release_baseline_approval_missing",
                                "communication": slug,
                                "journal_code": code,
                                "version": f"{current[0]}.{current[1]}",
                            }
                        )
                else:
                    blockers.append(
                        {
                            "reason": "communication_release_version_sequence_invalid",
                            "communication": slug,
                            "journal_code": code,
                            "version": f"{current[0]}.{current[1]}",
                            "previous": f"{previous[0]}.{previous[1]}",
                        }
                    )
                previous = current

        for row in release_tag_rows:
            if str(row["tag_kind"]) != "release":
                continue
            slug = str(row["product_slug"])
            code = str(row["journal_code"])
            release_date = str(row["release_date"] or "").strip()
            evidence_source = str(row["release_evidence_source"] or "").strip()
            evidence = str(row["release_evidence"] or "").strip()
            invalid_date = False
            try:
                parsed_release_date = datetime.strptime(release_date, "%Y-%m-%d").date()
                invalid_date = parsed_release_date > date.today()
            except ValueError:
                invalid_date = True
            if (
                invalid_date
                or evidence_source not in RELEASE_EVIDENCE_SOURCES
                or not evidence
            ):
                blockers.append(
                    {
                        "reason": "communication_public_release_evidence_invalid",
                        "communication": slug,
                        "journal_code": code,
                        "tag": str(row["tag_name"]),
                        "release_date": release_date,
                    }
                )

        release_rows_by_key = {
            (
                int(row["target_id"]),
                int(row["version_number"]),
                int(row["revision_number"]),
                str(row["tag_kind"]),
            ): row
            for row in release_tag_rows
        }
        registered_release_tags = {str(row["tag_name"]) for row in release_tag_rows}
        for release_tag in release_tag_rows:
            tag_name = str(release_tag["tag_name"])
            slug = str(release_tag["product_slug"])
            code = str(release_tag["journal_code"])
            version_number = int(release_tag["version_number"])
            revision_number = int(release_tag["revision_number"])
            tag_kind = str(release_tag["tag_kind"])
            release_date = str(release_tag["release_date"] or "").strip() or None
            expected_tag = f"{slug}/{code}-{version_number}.{revision_number}"
            if tag_kind == "release" and release_date:
                expected_tag += "-release-" + release_date.replace("-", "")
            parsed = parse_communication_tag(tag_name)
            if parsed is None or tag_name != expected_tag:
                blockers.append(
                    {
                        "reason": "communication_release_tag_name_invalid",
                        "communication": slug,
                        "journal_code": code,
                        "tag": tag_name,
                        "expected": expected_tag,
                    }
                )
                continue

            ref = f"refs/tags/{tag_name}"
            if run_git(project_root, "show-ref", "--verify", "--quiet", ref).returncode != 0:
                blockers.append(
                    {
                        "reason": "communication_release_tag_missing",
                        "communication": slug,
                        "journal_code": code,
                        "tag": tag_name,
                    }
                )
                continue
            object_type = run_git(project_root, "cat-file", "-t", ref)
            if object_type.returncode != 0 or object_type.stdout.strip() != "tag":
                blockers.append(
                    {
                        "reason": "communication_release_tag_not_annotated",
                        "communication": slug,
                        "journal_code": code,
                        "tag": tag_name,
                    }
                )
            object_oid = run_git(project_root, "rev-parse", "--verify", ref)
            current_object_oid = object_oid.stdout.strip() if object_oid.returncode == 0 else ""
            if current_object_oid != str(release_tag["tag_object_oid"]):
                blockers.append(
                    {
                        "reason": "communication_release_tag_object_changed",
                        "communication": slug,
                        "journal_code": code,
                        "tag": tag_name,
                        "recorded": str(release_tag["tag_object_oid"]),
                        "actual": current_object_oid,
                    }
                )
            peeled = run_git(project_root, "rev-parse", "--verify", f"{ref}^{{commit}}")
            current_commit = peeled.stdout.strip() if peeled.returncode == 0 else ""
            if current_commit != str(release_tag["commit_oid"]):
                blockers.append(
                    {
                        "reason": "communication_release_tag_commit_changed",
                        "communication": slug,
                        "journal_code": code,
                        "tag": tag_name,
                        "recorded": str(release_tag["commit_oid"]),
                        "actual": current_commit,
                    }
                )
            if tag_kind == "release":
                base = release_rows_by_key.get(
                    (int(release_tag["target_id"]), version_number, revision_number, "checkpoint")
                )
                if base is None:
                    blockers.append(
                        {
                            "reason": "communication_release_base_tag_missing",
                            "communication": slug,
                            "journal_code": code,
                            "tag": tag_name,
                        }
                    )
                elif str(base["commit_oid"]) != str(release_tag["commit_oid"]):
                    blockers.append(
                        {
                            "reason": "communication_release_commit_mismatch",
                            "communication": slug,
                            "journal_code": code,
                            "tag": tag_name,
                            "base_tag": str(base["tag_name"]),
                        }
                    )

        product_slugs = [
            str(row["slug"])
            for row in connection.execute("SELECT slug FROM communication_products ORDER BY id")
        ]
        for slug in product_slugs:
            listed = run_git(project_root, "tag", "--list", f"{slug}/*")
            if listed.returncode != 0:
                continue
            for tag_name in (line.strip() for line in listed.stdout.splitlines() if line.strip()):
                if parse_communication_tag(tag_name) is None:
                    blockers.append(
                        {
                            "reason": "communication_release_tag_name_invalid",
                            "communication": slug,
                            "tag": tag_name,
                        }
                    )
                elif tag_name not in registered_release_tags:
                    blockers.append(
                        {
                            "reason": "communication_release_tag_unregistered",
                            "communication": slug,
                            "tag": tag_name,
                        }
                    )

        derived_communication_paths = {
            str(row["path"])
            for row in artifact_rows
            if row["timing_role"] == "derived_output"
        }
        navigation_index_paths = human_navigation_index_paths(project_root)
        scientific_paths = [
            path
            for path in canonical_paths(project_root)
            if path not in {"RESEARCH.md", ".research/research.sqlite"}
            and path not in navigation_index_paths
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

from __future__ import annotations

from pathlib import Path
from typing import Any

from research_db_support.schema import HUMAN_ARTIFACT_LEGACY_BASELINE_META_KEY
from research_db_support.storage import ResearchDbError, connect, database_path

from .legacy import (
    legacy_baseline_commit,
    path_is_unchanged_since_baseline,
    validate_legacy_baseline,
)
from .validation import human_markdown_blockers, human_markdown_local_targets


HYPOTHESIS_H2 = (
    "Navigation",
    "Target Uncertainty",
    "Hypotheses",
    "Discriminator Matrix",
    "Current Evidence",
    "Decision Boundary",
)

DESIGN_H2 = (
    "Navigation",
    "Target Uncertainty",
    "Hypotheses and Discriminator",
    "Estimand / Target Contrast",
    "Population / Experimental System",
    "Sampling and Experimental Unit",
    "Groups / Exposure / Intervention / Comparator",
    "Measurements and Timepoints",
    "Controls and Bias Protection",
    "Primary Analysis Alignment",
    "Precision / Sample Size Rationale",
    "Decision Boundary",
    "Exploratory Analyses",
    "Feasibility / Ethics / Access Constraints",
    "Freeze and Amendments",
)

STUDY_H2 = (
    "Navigation",
    "Study Identity",
    "Source and Experimental Units",
    "Actual Groups / Exposure / Intervention",
    "Sample Collection and Processing",
    "Assays and Measurements",
    "Protocol / Materials / Instruments",
    "Batch / Run / Time",
    "Failures / Missing Events",
    "Deviations",
    "Outputs",
    "Record Boundary / Corrections",
)

DATASET_H2 = (
    "Navigation",
    "Dataset Identity",
    "Research Purpose",
    "Source and Version",
    "Population and Sample Mapping",
    "Data Layers and Artifacts",
    "Metadata / Missingness / Exclusions",
    "QC and Anomalies",
    "Processing and Reproduction",
    "Freeze / Access / Ethics",
)

ANALYSIS_H2 = (
    "Navigation",
    "Question / Target Contrast",
    "Inputs and Data Freeze",
    "Unit of Inference",
    "Primary Analysis",
    "Exploratory / Sensitivity Analyses",
    "Assumptions and Diagnostics",
    "Outputs",
    "Reproduction",
    "Result Boundary",
    "Amendments",
)

INTERPRETATION_H2 = (
    "Navigation",
    "Research Question",
    "Current Evidence State",
    "Supported",
    "Indirectly Supported",
    "Qualified",
    "Contradicted",
    "Unresolved",
    "Most Discriminating Next Evidence",
)


def _strict_artifact_blockers(
    project_root: Path,
    *,
    path: str,
    expected_path: str,
    h1_prefix: str,
    h2: tuple[str, ...],
    upstream_paths: list[str],
) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    artifact = project_root / path
    if not artifact.is_file():
        return [{"reason": "human_artifact_missing_file", "path": path}]
    if path != expected_path:
        blockers.append(
            {
                "reason": "human_artifact_path_invalid",
                "path": path,
                "expected": expected_path,
            }
        )

    _, format_blockers = human_markdown_blockers(
        project_root,
        path,
        expected_h1_prefix=h1_prefix,
        expected_h2=h2,
    )
    blockers.extend(format_blockers)
    navigation_targets = human_markdown_local_targets(project_root, path, section="Navigation")
    for target in upstream_paths:
        if target not in navigation_targets:
            blockers.append(
                {
                    "reason": "human_artifact_upstream_link_missing",
                    "path": path,
                    "target": target,
                }
            )
    return blockers


def _validate_artifact(
    project_root: Path,
    blockers: list[dict[str, Any]],
    *,
    path: str,
    expected_path: str,
    h1_prefix: str,
    h2: tuple[str, ...],
    upstream_paths: list[str],
    legacy_baseline: str | None,
    grandfathered_paths: list[str],
) -> None:
    artifact = project_root / path
    if artifact.is_file() and path_is_unchanged_since_baseline(
        project_root, artifact, legacy_baseline
    ):
        grandfathered_paths.append(path)
        return
    blockers.extend(
        _strict_artifact_blockers(
            project_root,
            path=path,
            expected_path=expected_path,
            h1_prefix=h1_prefix,
            h2=h2,
            upstream_paths=upstream_paths,
        )
    )


def _require_strict_artifact_before_freeze(
    project_root: Path,
    *,
    object_label: str,
    path: str,
    expected_path: str,
    h1_prefix: str,
    h2: tuple[str, ...],
    upstream_paths: list[str],
) -> None:
    blockers = _strict_artifact_blockers(
        project_root,
        path=path,
        expected_path=expected_path,
        h1_prefix=h1_prefix,
        h2=h2,
        upstream_paths=upstream_paths,
    )
    if not blockers:
        return
    reasons = ", ".join(dict.fromkeys(str(item.get("reason", "unknown")) for item in blockers))
    raise ResearchDbError(
        f"{object_label} 冻结前人类格式检查失败：{path}（{reasons}）；"
        "请先按 owner HUMAN-FORMAT.md 修正路径、固定章节与上游导航，再记录 freeze。"
    )


def require_hypothesis_human_format_before_freeze(
    project_root: Path,
    *,
    slug: str,
    artifact_path: str,
) -> None:
    _require_strict_artifact_before_freeze(
        project_root,
        object_label="Hypothesis Set",
        path=artifact_path,
        expected_path=f"hypotheses/{slug}.md",
        h1_prefix="Hypothesis Set: ",
        h2=HYPOTHESIS_H2,
        upstream_paths=["RESEARCH.md"],
    )


def require_design_human_format_before_freeze(
    project_root: Path,
    *,
    slug: str,
    artifact_path: str,
    hypothesis_path: str | None,
) -> None:
    upstream_paths = ["RESEARCH.md"]
    if hypothesis_path is not None:
        upstream_paths.append(hypothesis_path)
    _require_strict_artifact_before_freeze(
        project_root,
        object_label="Research Design",
        path=artifact_path,
        expected_path=f"designs/{slug}.md",
        h1_prefix="Design: ",
        h2=DESIGN_H2,
        upstream_paths=upstream_paths,
    )


def _validate_index(
    project_root: Path,
    blockers: list[dict[str, Any]],
    *,
    path: str,
    h1: str,
    object_paths: list[str],
    relation_paths: list[str],
) -> bool:
    if not object_paths:
        return False
    index = project_root / path
    if not index.is_file():
        blockers.append({"reason": "human_index_missing_file", "path": path})
        return False
    _, format_blockers = human_markdown_blockers(
        project_root,
        path,
        expected_h1=h1,
        expected_h2=("Objects", "Relations"),
    )
    blockers.extend(format_blockers)
    targets = human_markdown_local_targets(project_root, path, section="Objects")
    missing = sorted(set(object_paths) - targets)
    if missing:
        blockers.append(
            {
                "reason": "human_index_missing_object_link",
                "path": path,
                "targets": missing,
            }
        )
    relation_targets = human_markdown_local_targets(project_root, path, section="Relations")
    missing_relations = sorted(set(relation_paths) - relation_targets)
    if missing_relations:
        blockers.append(
            {
                "reason": "human_index_missing_relation_link",
                "path": path,
                "targets": missing_relations,
            }
        )
    return True


def core_human_artifact_readiness(project_root: Path) -> dict[str, Any]:
    db_path = database_path(project_root)
    if not db_path.exists():
        return {
            "ready": False,
            "checked": True,
            "blockers": [{"reason": "database_missing"}],
            "artifact_count": 0,
            "index_count": 0,
        }

    blockers: list[dict[str, Any]] = []
    recorded_legacy_baseline = legacy_baseline_commit(
        project_root, HUMAN_ARTIFACT_LEGACY_BASELINE_META_KEY
    )
    legacy_baseline, baseline_blocker = validate_legacy_baseline(
        project_root,
        recorded_legacy_baseline,
        invalid_reason="human_artifact_legacy_baseline_invalid",
        introduced_in_schema=24,
    )
    if baseline_blocker is not None:
        blockers.append(baseline_blocker)
    grandfathered_paths: list[str] = []
    artifact_count = 0
    index_count = 0
    with connect(db_path) as connection:
        tables = {
            str(row["name"])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
            )
        }

        hypothesis_paths: list[str] = []
        if "hypothesis_sets" in tables:
            for row in connection.execute(
                "SELECT slug, artifact_path FROM hypothesis_sets ORDER BY id"
            ):
                path = str(row["artifact_path"])
                hypothesis_paths.append(path)
                artifact_count += 1
                _validate_artifact(
                    project_root,
                    blockers,
                    path=path,
                    expected_path=f"hypotheses/{row['slug']}.md",
                    h1_prefix="Hypothesis Set: ",
                    h2=HYPOTHESIS_H2,
                    upstream_paths=["RESEARCH.md"],
                    legacy_baseline=legacy_baseline,
                    grandfathered_paths=grandfathered_paths,
                )
        hypothesis_relation_paths: list[str] = []
        design_paths: list[str] = []
        design_relation_paths: list[str] = []
        if "research_designs" in tables:
            for row in connection.execute(
                """
                SELECT d.id, d.slug, d.artifact_path, h.artifact_path AS hypothesis_path
                FROM research_designs d
                LEFT JOIN hypothesis_sets h ON h.id = d.hypothesis_set_id
                ORDER BY d.id
                """
            ):
                path = str(row["artifact_path"])
                design_paths.append(path)
                artifact_count += 1
                upstream = ["RESEARCH.md"]
                related = []
                if row["hypothesis_path"] is not None:
                    hypothesis_path = str(row["hypothesis_path"])
                    upstream.append(hypothesis_path)
                    related.append(hypothesis_path)
                    hypothesis_relation_paths.extend([hypothesis_path, path])
                related.extend(
                    str(item["provenance_path"])
                    for item in connection.execute(
                        "SELECT provenance_path FROM studies WHERE design_id = ? ORDER BY id",
                        (int(row["id"]),),
                    )
                )
                related.extend(
                    str(item["analysis_path"])
                    for item in connection.execute(
                        "SELECT analysis_path FROM analysis_runs WHERE design_id = ? ORDER BY id",
                        (int(row["id"]),),
                    )
                )
                if related:
                    design_relation_paths.extend([path, *related])
                _validate_artifact(
                    project_root,
                    blockers,
                    path=path,
                    expected_path=f"designs/{row['slug']}.md",
                    h1_prefix="Design: ",
                    h2=DESIGN_H2,
                    upstream_paths=upstream,
                    legacy_baseline=legacy_baseline,
                    grandfathered_paths=grandfathered_paths,
                )
        if _validate_index(
            project_root,
            blockers,
            path="hypotheses/README.md",
            h1="Hypotheses",
            object_paths=hypothesis_paths,
            relation_paths=hypothesis_relation_paths,
        ):
            index_count += 1
        if _validate_index(
            project_root,
            blockers,
            path="designs/README.md",
            h1="Designs",
            object_paths=design_paths,
            relation_paths=design_relation_paths,
        ):
            index_count += 1

        study_paths: list[str] = []
        study_relation_paths: list[str] = []
        if "studies" in tables:
            for row in connection.execute(
                """
                SELECT s.id, s.slug, s.provenance_path, d.artifact_path AS design_path
                FROM studies s
                LEFT JOIN research_designs d ON d.id = s.design_id
                ORDER BY s.id
                """
            ):
                path = str(row["provenance_path"])
                study_paths.append(path)
                artifact_count += 1
                upstream = ["RESEARCH.md"]
                related = []
                if row["design_path"] is not None:
                    design_path = str(row["design_path"])
                    upstream.append(design_path)
                    related.append(design_path)
                related.extend(
                    str(item["provenance_path"])
                    for item in connection.execute(
                        "SELECT provenance_path FROM datasets WHERE study_id = ? ORDER BY id",
                        (int(row["id"]),),
                    )
                )
                if related:
                    study_relation_paths.extend([path, *related])
                _validate_artifact(
                    project_root,
                    blockers,
                    path=path,
                    expected_path=f"study/{row['slug']}/README.md",
                    h1_prefix="Study: ",
                    h2=STUDY_H2,
                    upstream_paths=upstream,
                    legacy_baseline=legacy_baseline,
                    grandfathered_paths=grandfathered_paths,
                )
        if _validate_index(
            project_root,
            blockers,
            path="study/README.md",
            h1="Studies",
            object_paths=study_paths,
            relation_paths=study_relation_paths,
        ):
            index_count += 1

        dataset_paths: list[str] = []
        dataset_relation_paths: list[str] = []
        if "datasets" in tables:
            for row in connection.execute(
                """
                SELECT d.id, d.slug, d.provenance_path, s.provenance_path AS study_path
                FROM datasets d
                LEFT JOIN studies s ON s.id = d.study_id
                ORDER BY d.id
                """
            ):
                path = str(row["provenance_path"])
                dataset_paths.append(path)
                artifact_count += 1
                upstream = ["RESEARCH.md"]
                related = []
                if row["study_path"] is not None:
                    study_path = str(row["study_path"])
                    upstream.append(study_path)
                    related.append(study_path)
                related.extend(
                    str(item["analysis_path"])
                    for item in connection.execute(
                        """
                        SELECT a.analysis_path
                        FROM analysis_inputs ai
                        JOIN analysis_runs a ON a.id = ai.analysis_id
                        WHERE ai.dataset_id = ?
                        ORDER BY a.id
                        """,
                        (int(row["id"]),),
                    )
                )
                if related:
                    dataset_relation_paths.extend([path, *related])
                _validate_artifact(
                    project_root,
                    blockers,
                    path=path,
                    expected_path=f"data/{row['slug']}/README.md",
                    h1_prefix="Dataset: ",
                    h2=DATASET_H2,
                    upstream_paths=upstream,
                    legacy_baseline=legacy_baseline,
                    grandfathered_paths=grandfathered_paths,
                )
        if _validate_index(
            project_root,
            blockers,
            path="data/README.md",
            h1="Data",
            object_paths=dataset_paths,
            relation_paths=dataset_relation_paths,
        ):
            index_count += 1

        analysis_paths: list[str] = []
        analysis_relation_paths: list[str] = []
        if "analysis_runs" in tables:
            for row in connection.execute(
                """
                SELECT a.id, a.slug, a.analysis_path, d.artifact_path AS design_path
                FROM analysis_runs a
                LEFT JOIN research_designs d ON d.id = a.design_id
                ORDER BY a.id
                """
            ):
                path = str(row["analysis_path"])
                analysis_paths.append(path)
                artifact_count += 1
                upstream = ["RESEARCH.md"]
                if row["design_path"] is not None:
                    upstream.append(str(row["design_path"]))
                upstream.extend(
                    str(dataset["provenance_path"])
                    for dataset in connection.execute(
                        """
                        SELECT d.provenance_path
                        FROM analysis_inputs ai
                        JOIN datasets d ON d.id = ai.dataset_id
                        WHERE ai.analysis_id = ?
                        ORDER BY d.id
                        """,
                        (int(row["id"]),),
                    )
                )
                upstream = list(dict.fromkeys(upstream))
                if len(upstream) > 1:
                    analysis_relation_paths.extend([path, *upstream[1:]])
                _validate_artifact(
                    project_root,
                    blockers,
                    path=path,
                    expected_path=f"analysis/{row['slug']}/README.md",
                    h1_prefix="Analysis: ",
                    h2=ANALYSIS_H2,
                    upstream_paths=upstream,
                    legacy_baseline=legacy_baseline,
                    grandfathered_paths=grandfathered_paths,
                )
        if _validate_index(
            project_root,
            blockers,
            path="analysis/README.md",
            h1="Analyses",
            object_paths=analysis_paths,
            relation_paths=analysis_relation_paths,
        ):
            index_count += 1

    interpretation_dir = project_root / "interpretation"
    interpretation_paths: list[str] = []
    interpretation_relation_paths: list[str] = []
    if interpretation_dir.exists():
        nested = sorted(
            path.relative_to(project_root).as_posix()
            for path in interpretation_dir.rglob("*.md")
            if path.is_file() and path.parent != interpretation_dir
        )
        if nested:
            blockers.append(
                {
                    "reason": "interpretation_human_path_nested",
                    "paths": nested,
                }
            )
        for path_obj in sorted(interpretation_dir.glob("*.md")):
            if path_obj.name == "README.md":
                continue
            path = path_obj.relative_to(project_root).as_posix()
            interpretation_paths.append(path)
            artifact_count += 1
            if path_is_unchanged_since_baseline(project_root, path_obj, legacy_baseline):
                grandfathered_paths.append(path)
            else:
                _, format_blockers = human_markdown_blockers(
                    project_root,
                    path,
                    expected_h1_prefix="Interpretation: ",
                    expected_h2=INTERPRETATION_H2,
                )
                blockers.extend(format_blockers)
                navigation = human_markdown_local_targets(
                    project_root,
                    path,
                    section="Navigation",
                )
                if "RESEARCH.md" not in navigation:
                    blockers.append(
                        {
                            "reason": "human_artifact_upstream_link_missing",
                            "path": path,
                            "target": "RESEARCH.md",
                        }
                    )
                related = sorted(navigation - {"RESEARCH.md", "interpretation/README.md"})
                if not related:
                    blockers.append(
                        {
                            "reason": "interpretation_upstream_link_missing",
                            "path": path,
                        }
                    )
                else:
                    interpretation_relation_paths.extend([path, *related])
    if _validate_index(
        project_root,
        blockers,
        path="interpretation/README.md",
        h1="Interpretations",
        object_paths=interpretation_paths,
        relation_paths=interpretation_relation_paths,
    ):
        index_count += 1

    return {
        "ready": not blockers,
        "checked": True,
        "blockers": blockers,
        "artifact_count": artifact_count,
        "index_count": index_count,
        "legacy_baseline_commit": recorded_legacy_baseline,
        "legacy_baseline_valid": baseline_blocker is None,
        "grandfathered_paths": sorted(grandfathered_paths),
    }

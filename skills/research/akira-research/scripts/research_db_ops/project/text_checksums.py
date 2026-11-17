"""Redact redundant SHA256 values embedded in human-readable free-text fields."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import research_db_ops.common as common
from research_db_support.storage import connect


TEXT_CHECKSUM_PLACEHOLDER = "［已移除冗余校验值］"
# A standalone 64-hex run, optionally prefixed with ``sha256:``. Neighbouring
# ASCII letters or digits disqualify a match, so 40-hex Git commit ids, longer
# hex runs and identifiers that merely contain a hash are left untouched.
TEXT_CHECKSUM_RE = re.compile(
    r"(?<![0-9A-Za-z])(?:[Ss][Hh][Aa]256:)?[0-9a-fA-F]{64}(?![0-9A-Za-z])"
)
# Human explanation / reason / summary prose columns that may be redacted.
# Identity, path, slug, commit/ref, version, JSON, dedicated sha256 columns,
# verbatim user/paper quotations, literature extraction tables and change_log
# are deliberately excluded.
TEXT_CHECKSUM_COLUMNS: dict[str, tuple[str, ...]] = {
    "acquisition_attempts": ("detail", "supersession_reason", "access_basis_detail"),
    "analysis_amendments": ("description", "reason"),
    "analysis_artifacts": ("tracking_reason",),
    "analysis_attempts": ("reason", "decision_reason"),
    "analysis_dataset_artifact_timing": ("reason",),
    "analysis_runs": ("target_uncertainty", "estimand", "unit_of_inference", "primary_analysis"),
    "candidates": ("relevance_reason", "exclusion_reason", "defer_reason", "user_access_reason"),
    "communication_artifacts": ("tracking_reason",),
    "communication_products": ("purpose",),
    "communication_release_tags": ("baseline_approval", "release_evidence"),
    "dataset_artifacts": ("tracking_reason",),
    "freeze_revisions": ("reason",),
    "hypothesis_evaluations": ("decision", "summary"),
    "hypothesis_proposals": ("operationalized_statement", "rationale", "source_context"),
    "path_migrations": ("reason",),
    "project_observations": ("statement", "effect", "scope"),
    "reading_runs": ("notes",),
    "relations": ("note",),
    "research_designs": ("target_estimand", "primary_outcome", "experimental_unit", "feasibility_summary"),
    "research_edges": ("note",),
    "research_git_branches": ("closure_reason",),
    "research_judgments": ("statement", "basis"),
    "research_nodes": ("scientific_scope", "closure_reason"),
    "search_runs": ("purpose", "reason", "what_we_learned", "next_decision"),
    "study_artifacts": ("tracking_reason",),
    "study_deviations": ("description", "reason", "affected_units", "scientific_impact"),
    "user_hypothesis_decisions": ("rationale",),
}


def _existing_columns(connection, table: str) -> set[str]:
    return {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}


def _text_checksum_hits(connection) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for table, columns in TEXT_CHECKSUM_COLUMNS.items():
        present = [column for column in columns if column in _existing_columns(connection, table)]
        for column in present:
            query = (
                f"SELECT rowid AS row_id, {column} AS value FROM {table}"
                f" WHERE {column} IS NOT NULL ORDER BY rowid"
            )
            for row in connection.execute(query):
                value = row["value"]
                if not isinstance(value, str):
                    continue
                checksums = TEXT_CHECKSUM_RE.findall(value)
                if checksums:
                    hits.append(
                        {
                            "table": table,
                            "row_id": row["row_id"],
                            "column": column,
                            "checksums": checksums,
                            "old_value": value,
                            "new_value": TEXT_CHECKSUM_RE.sub(TEXT_CHECKSUM_PLACEHOLDER, value),
                        }
                    )
    return hits


def redact_text_checksums(
    project_root: Path, *, reason: str | None = None, dry_run: bool = False
) -> dict[str, Any]:
    """Replace standalone SHA256 values in prose columns with a fixed placeholder.

    Git-tracked objects are identified by commit + path and untracked artifacts
    keep their checksum in the dedicated ``sha256`` column, so a hash written
    into explanation text is redundant. Each changed cell writes one change_log
    entry that keeps the removed values; ``dry_run`` only lists the cells.
    """

    note = common.text(reason) or (
        "自由文本中的校验值冗余：Git 跟踪对象以提交号 + 路径识别，"
        "未跟踪 artifact 校验值保存在 sha256 字段。"
    )
    now = common.now()
    with connect(common.db_path(project_root)) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            hits = _text_checksum_hits(connection)
            if dry_run:
                connection.rollback()
            else:
                for hit in hits:
                    connection.execute(
                        f"UPDATE {hit['table']} SET {hit['column']} = ? WHERE rowid = ?",
                        (hit["new_value"], hit["row_id"]),
                    )
                    summary = (
                        f"table={hit['table']}; row_id={hit['row_id']}; column={hit['column']}; "
                        f"old_values={', '.join(hit['checksums'])}"
                    )
                    connection.execute(
                        """
                        INSERT INTO change_log(timestamp, action, entity_type, entity_id, reason, summary)
                        VALUES (?, 'text_checksum_redacted', ?, ?, ?, ?)
                        """,
                        (now, hit["table"], str(hit["row_id"]), note, summary),
                    )
                connection.commit()
        except Exception:
            connection.rollback()
            raise
    counts: dict[str, int] = {}
    for hit in hits:
        key = f"{hit['table']}.{hit['column']}"
        counts[key] = counts.get(key, 0) + len(hit["checksums"])
    return {
        "ok": True,
        "dry_run": dry_run,
        "placeholder": TEXT_CHECKSUM_PLACEHOLDER,
        "cell_count": len(hits),
        "checksum_count": sum(len(hit["checksums"]) for hit in hits),
        "counts": counts,
        "redactions": hits,
    }

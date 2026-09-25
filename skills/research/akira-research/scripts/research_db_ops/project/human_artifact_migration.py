from __future__ import annotations

from pathlib import Path
from typing import Any

import research_db_ops.common as common
from research_db_support.storage import ResearchDbError, connect


_ENTITY_SPECS = {
    "dataset": {
        "table": "datasets",
        "path_field": "provenance_path",
        "expected_path": lambda slug: f"data/{slug}/README.md",
    },
    "analysis": {
        "table": "analysis_runs",
        "path_field": "analysis_path",
        "expected_path": lambda slug: f"analysis/{slug}/README.md",
    },
}


def migrate_human_artifact_path(project_root: Path, bundle: dict[str, Any]) -> dict[str, Any]:
    """Move only the canonical human-readable pointer for an existing object.

    Scientific identity, workflow status, inputs, outputs, estimates and all other
    provenance fields remain untouched. This narrow operator exists for adopting
    the fixed human-artifact contract after an object was already registered.
    """

    entity_type = common.enum_value(
        bundle.get("entity_type"),
        set(_ENTITY_SPECS),
        default="",
        field="entity_type",
    )
    slug = common.slug(bundle.get("slug"))
    new_path = common.local_path(
        project_root,
        bundle.get("new_path"),
        field="new_path",
        require_file=True,
    )
    reason = common.text(bundle.get("reason"), required=True, field="reason")
    assert reason is not None

    spec = _ENTITY_SPECS[entity_type]
    expected_path = spec["expected_path"](slug)
    if new_path != expected_path:
        raise ResearchDbError(
            f"{entity_type}={slug} 的 canonical human artifact 必须迁移到 "
            f"{expected_path}；收到 {new_path}。"
        )

    table = str(spec["table"])
    path_field = str(spec["path_field"])
    now = common.now()

    with connect(common.db_path(project_root)) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            row = connection.execute(
                f"SELECT id, {path_field} FROM {table} WHERE slug = ?",
                (slug,),
            ).fetchone()
            if row is None:
                raise ResearchDbError(
                    f"human artifact path migration 引用不存在的 {entity_type}：{slug}"
                )

            entity_id = int(row["id"])
            old_path = str(row[path_field])
            if old_path != new_path:
                connection.execute(
                    f"UPDATE {table} SET {path_field} = ?, updated_at = ? WHERE id = ?",
                    (new_path, now, entity_id),
                )
                connection.execute(
                    """
                    INSERT INTO change_log(
                        timestamp, action, entity_type, entity_id, reason, summary
                    ) VALUES (?, 'human_artifact_path_migrated', ?, ?, ?, ?)
                    """,
                    (
                        now,
                        entity_type,
                        str(entity_id),
                        reason,
                        f"slug={slug}; old_path={old_path}; new_path={new_path}",
                    ),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise

    return {
        "ok": True,
        "entity_type": entity_type,
        "slug": slug,
        "old_path": old_path,
        "new_path": new_path,
        "migrated": old_path != new_path,
    }

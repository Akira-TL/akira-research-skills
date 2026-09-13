from __future__ import annotations

from pathlib import Path
from typing import Any

from research_db_support.storage import ResearchDbError, connect
import research_db_ops.common as common


COMMUNICATION_STATUSES = {"draft", "completed", "superseded"}
COMMUNICATION_ROLES = {
    "title_abstract",
    "methods",
    "results",
    "discussion",
    "figure",
    "figure_legend",
    "table",
    "lay_summary",
    "traceability",
    "generator",
    "other",
}
COMMUNICATION_TIMING_ROLES = {"source_support", "derived_output"}
HUMAN_COMMUNICATION_ROOT = "communication"
INTERNAL_COMMUNICATION_ROOT = ".research/communication"


def _project_relative_path(project_root: Path, value: object, *, field: str) -> str:
    raw = common.text(value, required=True, field=field)
    assert raw is not None
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = project_root / path
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(project_root.resolve())
    except ValueError as exc:
        raise ResearchDbError(f"{field} 必须位于科研项目目录内：{resolved}") from exc
    return relative.as_posix()


def _artifact_matches_product_workspace(path: str, slug: str) -> bool:
    return path.startswith(f"{HUMAN_COMMUNICATION_ROOT}/{slug}/") or path.startswith(
        f"{INTERNAL_COMMUNICATION_ROOT}/{slug}/"
    )


def record_communication(project_root: Path, bundle: dict[str, Any]) -> dict[str, Any]:
    slug = common.slug(bundle.get("slug"))
    title = common.text(bundle.get("title"), required=True, field="title")
    purpose = common.text(bundle.get("purpose"), required=True, field="purpose")
    audience = common.text(bundle.get("audience"), required=True, field="audience")
    source_commit = common.text(bundle.get("source_commit"), required=True, field="source_commit")
    status = common.enum_value(bundle.get("status"), COMMUNICATION_STATUSES, default="draft", field="status")
    artifacts = bundle.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ResearchDbError("communication artifacts 必须是非空数组。")

    parsed: list[dict[str, Any]] = []
    for index, item in enumerate(artifacts, start=1):
        if not isinstance(item, dict):
            raise ResearchDbError(f"communication artifact {index} 必须是 JSON object。")
        role = common.enum_value(item.get("role"), COMMUNICATION_ROLES, default="other", field="communication artifact role")
        path = common.local_path(project_root, item.get("path"), field="communication artifact path")
        timing_role = common.enum_value(
            item.get("timing_role"),
            COMMUNICATION_TIMING_ROLES,
            default="derived_output",
            field="communication artifact timing_role",
        )
        git_tracking = common.tracking(item.get("git_tracking"))
        tracking_reason = common.text(item.get("tracking_reason"))
        if git_tracking == "not_required" and not tracking_reason:
            raise ResearchDbError("communication artifact git_tracking=not_required 时必须说明 tracking_reason。")
        parsed.append(
            {
                "role": role,
                "path": path,
                "timing_role": timing_role,
                "git_tracking": git_tracking,
                "tracking_reason": tracking_reason,
            }
        )

    assert title is not None and purpose is not None and audience is not None and source_commit is not None
    now = common.now()
    with connect(common.db_path(project_root)) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            existing = connection.execute(
                "SELECT * FROM communication_products WHERE slug = ?", (slug,)
            ).fetchone()
            if existing is None:
                cursor = connection.execute(
                    """
                    INSERT INTO communication_products(
                        slug, title, purpose, audience, source_commit, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (slug, title, purpose, audience, source_commit, status, now, now),
                )
                product_id = int(cursor.lastrowid)
            else:
                product_id = int(existing["id"])
                if existing["status"] == "completed":
                    immutable = ("title", "purpose", "audience", "source_commit")
                    changed = [
                        field
                        for field, value in zip(immutable, (title, purpose, audience, source_commit))
                        if str(existing[field]) != str(value)
                    ]
                    if changed:
                        raise ResearchDbError(
                            "completed Communication Product 不能静默修改来源或定义字段："
                            + ", ".join(changed)
                        )
                    if status != "completed":
                        raise ResearchDbError("completed Communication Product 不能回退状态。")
                if existing["status"] == "superseded":
                    raise ResearchDbError("superseded Communication Product 不能重新激活。")
                connection.execute(
                    """
                    UPDATE communication_products
                    SET title = ?, purpose = ?, audience = ?, source_commit = ?, status = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (title, purpose, audience, source_commit, status, now, product_id),
                )

            for item in parsed:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO communication_artifacts(
                        product_id, role, path, timing_role, git_tracking, tracking_reason, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        product_id,
                        item["role"],
                        item["path"],
                        item["timing_role"],
                        item["git_tracking"],
                        item["tracking_reason"],
                        now,
                    ),
                )

            connection.execute(
                """
                INSERT INTO change_log(timestamp, action, entity_type, entity_id, reason, summary)
                VALUES (?, 'communication_recorded', 'communication_product', ?, ?, ?)
                """,
                (
                    now,
                    str(product_id),
                    f"Communication Product state recorded as {status}.",
                    f"communication={slug}; status={status}; artifacts={len(parsed)}; source_commit={source_commit}",
                ),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
    return {"ok": True, "communication_id": product_id, "slug": slug, "status": status}


def relocate_communication_artifact(project_root: Path, bundle: dict[str, Any]) -> dict[str, Any]:
    slug = common.slug(bundle.get("slug"))
    old_path = _project_relative_path(project_root, bundle.get("old_path"), field="old_path")
    new_path = common.local_path(
        project_root,
        bundle.get("new_path"),
        field="new_path",
        require_file=True,
    )
    reason = common.text(bundle.get("reason"), required=True, field="reason")
    assert reason is not None

    if (project_root / old_path).exists():
        raise ResearchDbError(
            f"旧路径仍然存在：{old_path}；relocate 只同步已经完成的文件系统迁移，不能把复制当作迁移。"
        )
    if old_path == new_path:
        raise ResearchDbError("old_path 与 new_path 不能相同。")

    now = common.now()
    with connect(common.db_path(project_root)) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            product = connection.execute(
                "SELECT * FROM communication_products WHERE slug = ?", (slug,)
            ).fetchone()
            if product is None:
                raise ResearchDbError(f"Communication Product 不存在：{slug}")

            artifact = connection.execute(
                """
                SELECT * FROM communication_artifacts
                WHERE product_id = ? AND path = ?
                """,
                (int(product["id"]), old_path),
            ).fetchone()
            if artifact is None:
                raise ResearchDbError(
                    f"Communication Product {slug} 没有登记旧 artifact 路径：{old_path}"
                )

            if product["status"] == "completed" and artifact["timing_role"] == "source_support":
                raise ResearchDbError(
                    "completed Communication Product 的 source_support artifact 不能通过路径 relocation 改写；"
                    "其路径必须继续能由 pre-communication source commit 证明。"
                )

            if artifact["timing_role"] == "derived_output" and artifact["role"] != "generator":
                if not _artifact_matches_product_workspace(new_path, slug):
                    raise ResearchDbError(
                        f"Communication Product {slug} 的非 generator 派生 artifact 必须迁入 "
                        f"communication/{slug}/ 或 .research/communication/{slug}/：{new_path}"
                    )

            conflict = connection.execute(
                """
                SELECT id FROM communication_artifacts
                WHERE product_id = ? AND path = ? AND id <> ?
                """,
                (int(product["id"]), new_path, int(artifact["id"])),
            ).fetchone()
            if conflict is not None:
                raise ResearchDbError(
                    f"Communication Product {slug} 已登记目标 artifact 路径：{new_path}"
                )

            connection.execute(
                "UPDATE communication_artifacts SET path = ? WHERE id = ?",
                (new_path, int(artifact["id"])),
            )
            connection.execute(
                "UPDATE communication_products SET updated_at = ? WHERE id = ?",
                (now, int(product["id"])),
            )
            connection.execute(
                """
                INSERT INTO change_log(timestamp, action, entity_type, entity_id, reason, summary)
                VALUES (?, 'communication_artifact_relocated', 'communication_artifact', ?, ?, ?)
                """,
                (
                    now,
                    str(artifact["id"]),
                    reason,
                    f"communication={slug}; old_path={old_path}; new_path={new_path}",
                ),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise

    return {
        "ok": True,
        "communication_id": int(product["id"]),
        "artifact_id": int(artifact["id"]),
        "slug": slug,
        "old_path": old_path,
        "new_path": new_path,
    }


def list_communications(project_root: Path, *, limit: int = 100) -> dict[str, Any]:
    with connect(common.db_path(project_root)) as connection:
        rows: list[dict[str, Any]] = []
        for row in connection.execute(
            "SELECT * FROM communication_products ORDER BY id LIMIT ?", (limit,)
        ):
            item = dict(row)
            item["artifacts"] = [
                dict(x)
                for x in connection.execute(
                    "SELECT * FROM communication_artifacts WHERE product_id = ? ORDER BY id",
                    (row["id"],),
                )
            ]
            rows.append(item)
    return {"ok": True, "communications": rows}

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

from research_db_support.storage import ResearchDbError, connect
import research_db_ops.common as common
from .target import (
    canonical_source_path,
    file_content_oid,
    journal_code,
    journal_name_key,
    load_target_manifest,
    manifest_path,
    workspace_path,
)


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
    canonical_source_requested = bundle.get("canonical_source_path") is not None
    canonical_source = (
        canonical_source_path(project_root, slug, bundle.get("canonical_source_path"))
        if canonical_source_requested
        else None
    )
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

    if canonical_source is not None:
        canonical_artifact = next(
            (item for item in parsed if item["path"] == canonical_source),
            None,
        )
        if canonical_artifact is None:
            raise ResearchDbError(
                "canonical_source_path 必须同时登记为当前 Communication Product 的 artifact。"
            )
        if canonical_artifact["git_tracking"] != "required":
            raise ResearchDbError("canonical communication source 必须由 Git 跟踪。")

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
                        slug, title, purpose, audience, source_commit, status,
                        canonical_source_path, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        slug,
                        title,
                        purpose,
                        audience,
                        source_commit,
                        status,
                        canonical_source,
                        now,
                        now,
                    ),
                )
                product_id = int(cursor.lastrowid)
                effective_canonical_source = canonical_source
            else:
                product_id = int(existing["id"])
                existing_canonical = (
                    str(existing["canonical_source_path"])
                    if existing["canonical_source_path"] is not None
                    else None
                )
                effective_canonical_source = (
                    canonical_source if canonical_source_requested else existing_canonical
                )
                if existing["status"] == "completed":
                    immutable = (
                        "title",
                        "purpose",
                        "audience",
                        "source_commit",
                        "canonical_source_path",
                    )
                    values = (
                        title,
                        purpose,
                        audience,
                        source_commit,
                        effective_canonical_source,
                    )
                    changed = [
                        field
                        for field, value in zip(immutable, values)
                        if (existing[field] if existing[field] is not None else None) != value
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
                    SET title = ?, purpose = ?, audience = ?, source_commit = ?, status = ?,
                        canonical_source_path = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        title,
                        purpose,
                        audience,
                        source_commit,
                        status,
                        effective_canonical_source,
                        now,
                        product_id,
                    ),
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
    return {
        "ok": True,
        "communication_id": product_id,
        "slug": slug,
        "status": status,
        "canonical_source_path": effective_canonical_source,
    }


def record_journal(project_root: Path, bundle: dict[str, Any]) -> dict[str, Any]:
    code = journal_code(bundle.get("code"))
    name = common.text(bundle.get("name"), required=True, field="journal name")
    official_source = common.text(
        bundle.get("official_source"), required=True, field="journal official_source"
    )
    checked_at = common.parse_timestamp(bundle.get("checked_at"), field="journal checked_at").isoformat()
    assert name is not None and official_source is not None
    name_key = journal_name_key(name)
    if not name_key:
        raise ResearchDbError("journal name 必须包含可识别字符。")

    now = common.now()
    with connect(common.db_path(project_root)) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            by_code = connection.execute(
                "SELECT * FROM communication_journals WHERE code = ? COLLATE NOCASE",
                (code,),
            ).fetchone()
            by_name = connection.execute(
                "SELECT * FROM communication_journals WHERE name_key = ?",
                (name_key,),
            ).fetchone()
            if by_code is not None and str(by_code["name_key"]) != name_key:
                raise ResearchDbError(
                    f"期刊代码 {code} 已经登记给 {by_code['name']}；不能复用为 {name}。"
                )
            if by_name is not None and str(by_name["code"]) != code:
                raise ResearchDbError(
                    f"期刊 {name} 已经登记为代码 {by_name['code']}；不能再创建别名 {code}。"
                )
            if by_code is None:
                connection.execute(
                    """
                    INSERT INTO communication_journals(
                        code, name, name_key, official_source, checked_at, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (code, name, name_key, official_source, checked_at, now, now),
                )
            else:
                if str(by_code["code"]) != code:
                    raise ResearchDbError(
                        f"期刊代码必须沿用已登记拼写 {by_code['code']}，不能改成 {code}。"
                    )
                connection.execute(
                    """
                    UPDATE communication_journals
                    SET official_source = ?, checked_at = ?, updated_at = ?
                    WHERE code = ?
                    """,
                    (official_source, checked_at, now, code),
                )
            connection.execute(
                """
                INSERT INTO change_log(timestamp, action, entity_type, entity_id, reason, summary)
                VALUES (?, 'communication_journal_recorded', 'communication_journal', ?, ?, ?)
                """,
                (
                    now,
                    code,
                    "Stable target journal code recorded or refreshed.",
                    f"journal={name}; code={code}; checked_at={checked_at}",
                ),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
    return {
        "ok": True,
        "code": code,
        "name": name,
        "official_source": official_source,
        "checked_at": checked_at,
    }


def _require_git_source_commit(project_root: Path, source_commit: str, canonical_source: str) -> None:
    commit = subprocess.run(
        ["git", "-C", str(project_root), "cat-file", "-e", f"{source_commit}^{{commit}}"],
        capture_output=True,
        check=False,
    )
    if commit.returncode != 0:
        raise ResearchDbError(f"target source_commit 不是可用 Git commit：{source_commit}")
    ancestor = subprocess.run(
        ["git", "-C", str(project_root), "merge-base", "--is-ancestor", source_commit, "HEAD"],
        capture_output=True,
        check=False,
    )
    if ancestor.returncode != 0:
        raise ResearchDbError("target source_commit 必须是当前 HEAD 的祖先。")
    source = subprocess.run(
        ["git", "-C", str(project_root), "cat-file", "-e", f"{source_commit}:{canonical_source}"],
        capture_output=True,
        check=False,
    )
    if source.returncode != 0:
        raise ResearchDbError(
            f"target source_commit 中不存在 canonical communication source：{canonical_source}"
        )


def record_target_workspace(project_root: Path, bundle: dict[str, Any]) -> dict[str, Any]:
    slug = common.slug(bundle.get("slug"))
    requested_code = journal_code(bundle.get("journal_code"))
    source_commit = common.text(
        bundle.get("source_commit"), required=True, field="target source_commit"
    )
    assert source_commit is not None

    with connect(common.db_path(project_root)) as connection:
        product = connection.execute(
            "SELECT * FROM communication_products WHERE slug = ?",
            (slug,),
        ).fetchone()
        if product is None:
            raise ResearchDbError(f"Communication Product 不存在：{slug}")
        journal = connection.execute(
            "SELECT * FROM communication_journals WHERE code = ? COLLATE NOCASE",
            (requested_code,),
        ).fetchone()
        if journal is None:
            raise ResearchDbError(
                f"目标期刊代码尚未登记：{requested_code}；先运行 record-journal。"
            )
        code = str(journal["code"])
        if code != requested_code:
            raise ResearchDbError(
                f"目标期刊代码必须使用已登记拼写 {code}，不能使用 {requested_code}。"
            )
        canonical_source = str(product["canonical_source_path"] or "").strip()
        if not canonical_source:
            raise ResearchDbError(
                "创建 target release workspace 前必须先为 Communication Product 登记 canonical_source_path。"
            )
        product_id = int(product["id"])

    _require_git_source_commit(project_root, source_commit, canonical_source)
    manifest = load_target_manifest(
        project_root,
        slug=slug,
        code=code,
        expected_canonical_source=canonical_source,
        expected_source_commit=source_commit,
    )
    file_rows = [
        (kind, path, file_content_oid(project_root, path))
        for kind, path in manifest["files"]
    ]
    expected_workspace = workspace_path(slug, code)
    expected_manifest = manifest_path(slug, code)
    now = common.now()

    with connect(common.db_path(project_root)) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            existing = connection.execute(
                """
                SELECT * FROM communication_target_workspaces
                WHERE product_id = ? AND journal_code = ?
                """,
                (product_id, code),
            ).fetchone()
            if existing is None:
                cursor = connection.execute(
                    """
                    INSERT INTO communication_target_workspaces(
                        product_id, journal_code, workspace_path, manifest_path,
                        source_commit, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        product_id,
                        code,
                        expected_workspace,
                        expected_manifest,
                        source_commit,
                        now,
                        now,
                    ),
                )
                target_id = int(cursor.lastrowid)
            else:
                target_id = int(existing["id"])
                if str(existing["workspace_path"]) != expected_workspace:
                    raise ResearchDbError(
                        "已登记 target release workspace identity 与 journal code 不一致；不能移动或创建别名目录。"
                    )
                if str(existing["manifest_path"]) != expected_manifest:
                    raise ResearchDbError("target release manifest 固定为 <journal-code>-release/manifest.json。")
                connection.execute(
                    """
                    UPDATE communication_target_workspaces
                    SET source_commit = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (source_commit, now, target_id),
                )

            connection.execute(
                "DELETE FROM communication_target_files WHERE target_id = ?",
                (target_id,),
            )
            for kind, path, oid in file_rows:
                connection.execute(
                    """
                    INSERT INTO communication_target_files(
                        target_id, kind, path, content_oid, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (target_id, kind, path, oid, now),
                )
            connection.execute(
                """
                INSERT INTO change_log(timestamp, action, entity_type, entity_id, reason, summary)
                VALUES (?, 'communication_target_recorded', 'communication_target_workspace', ?, ?, ?)
                """,
                (
                    now,
                    str(target_id),
                    "Target journal build workspace recorded from canonical communication source.",
                    f"communication={slug}; journal={code}; source_commit={source_commit}",
                ),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise

    return {
        "ok": True,
        "target_id": target_id,
        "slug": slug,
        "journal_code": code,
        "workspace_path": expected_workspace,
        "manifest_path": expected_manifest,
        "canonical_source_path": canonical_source,
        "source_commit": source_commit,
        "target_files": [path for _, path, _ in file_rows],
    }


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
            targets: list[dict[str, Any]] = []
            for target in connection.execute(
                """
                SELECT ctw.*, cj.name AS journal_name,
                       cj.official_source AS journal_official_source,
                       cj.checked_at AS journal_checked_at
                FROM communication_target_workspaces AS ctw
                JOIN communication_journals AS cj ON cj.code = ctw.journal_code
                WHERE ctw.product_id = ?
                ORDER BY ctw.id
                """,
                (row["id"],),
            ):
                target_item = dict(target)
                target_item["canonical_source_path"] = item.get("canonical_source_path")
                target_item["files"] = [
                    dict(x)
                    for x in connection.execute(
                        "SELECT * FROM communication_target_files WHERE target_id = ? ORDER BY id",
                        (target["id"],),
                    )
                ]
                target_item["release_tags"] = [
                    dict(x)
                    for x in connection.execute(
                        "SELECT * FROM communication_release_tags WHERE target_id = ? ORDER BY version_number, revision_number, tag_kind",
                        (target["id"],),
                    )
                ]
                targets.append(target_item)
            item["target_workspaces"] = targets
            rows.append(item)
    return {"ok": True, "communications": rows}

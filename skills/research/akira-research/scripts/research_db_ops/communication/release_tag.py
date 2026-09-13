from __future__ import annotations

import re
import subprocess
from datetime import date, datetime
from pathlib import Path
from typing import Any

import research_db_ops.common as common
from research_db_ops.communication.target import (
    load_target_manifest,
    stored_generated_outputs,
    verify_target_build,
)
from research_db_support.storage import ResearchDbError, connect


VERSION_RE = re.compile(r"^([1-9][0-9]*)\.([0-9]+)$")
TAG_RE = re.compile(
    r"^(?P<article>[a-z0-9][a-z0-9-]*)/(?P<journal>[A-Za-z][A-Za-z0-9]{0,15})-"
    r"(?P<version>[1-9][0-9]*)\.(?P<revision>[0-9]+)"
    r"(?:-release-(?P<release_date>[0-9]{8}))?$"
)
BASELINE_APPROVAL_SOURCES = {"user", "project_decision"}
RELEASE_EVIDENCE_SOURCES = {"user_confirmation", "public_source"}


def _git(project_root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(project_root), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown git error"
        raise ResearchDbError(f"Git 命令失败：git {' '.join(args)}：{detail}")
    return result


def parse_release_version(value: object) -> tuple[int, int, str]:
    raw = common.text(value, required=True, field="communication release version")
    assert raw is not None
    match = VERSION_RE.fullmatch(raw)
    if match is None:
        raise ResearchDbError(
            "稿件版本必须使用两段“版本号.修订号”，例如 1.0、1.1、2.0；"
            "这不是 SemVer，不允许 v 前缀或第三段 patch。"
        )
    version_number = int(match.group(1))
    revision_number = int(match.group(2))
    canonical = f"{version_number}.{revision_number}"
    if raw != canonical:
        raise ResearchDbError(
            f"稿件版本必须使用规范十进制形式 {canonical}，不得保留前导零。"
        )
    return version_number, revision_number, canonical


def parse_communication_tag(tag_name: str) -> dict[str, Any] | None:
    match = TAG_RE.fullmatch(tag_name)
    if match is None:
        return None
    release_raw = match.group("release_date")
    return {
        "article": match.group("article"),
        "journal_code": match.group("journal"),
        "version_number": int(match.group("version")),
        "revision_number": int(match.group("revision")),
        "release_date": (
            f"{release_raw[:4]}-{release_raw[4:6]}-{release_raw[6:]}" if release_raw else None
        ),
    }


def _require_clean_worktree(project_root: Path) -> None:
    status = _git(project_root, "status", "--porcelain", "--untracked-files=normal")
    if status.stdout.strip():
        raise ResearchDbError(
            "创建正式 manuscript tag 前工作树必须 clean；先提交 canonical source、target workspace、"
            "manifest、build source 与 QA 依据。"
        )


def _tag_exists(project_root: Path, tag_name: str) -> bool:
    return (
        _git(
            project_root,
            "show-ref",
            "--verify",
            "--quiet",
            f"refs/tags/{tag_name}",
            check=False,
        ).returncode
        == 0
    )


def _head_commit(project_root: Path) -> str:
    result = _git(project_root, "rev-parse", "--verify", "HEAD^{commit}")
    return result.stdout.strip()


def _require_tracked_at_head(project_root: Path, paths: list[str]) -> None:
    missing: list[str] = []
    for path in paths:
        tracked = _git(project_root, "ls-files", "--error-unmatch", "--", path, check=False)
        present = _git(project_root, "cat-file", "-e", f"HEAD:{path}", check=False)
        if tracked.returncode != 0 or present.returncode != 0:
            missing.append(path)
    if missing:
        raise ResearchDbError(
            "创建正式 manuscript checkpoint 前，canonical source 与 target build source 必须已经提交到 HEAD："
            + ", ".join(sorted(set(missing)))
        )


def _tag_object_oid(project_root: Path, tag_name: str) -> str:
    result = _git(project_root, "rev-parse", "--verify", f"refs/tags/{tag_name}")
    return result.stdout.strip()


def _tag_commit(project_root: Path, tag_name: str) -> str:
    result = _git(project_root, "rev-parse", "--verify", f"refs/tags/{tag_name}^{{commit}}")
    return result.stdout.strip()


def _release_date(value: object) -> str:
    raw = common.text(value, required=True, field="release_date")
    assert raw is not None
    try:
        parsed = datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ResearchDbError("release_date 必须使用 YYYY-MM-DD。") from exc
    if parsed > date.today():
        raise ResearchDbError("公开 release 日期不能位于未来；只有已经真实公开的版本才能创建 release tag。")
    return parsed.isoformat()


def _checkpoint_sequence(
    connection: Any,
    target_id: int,
    *,
    version_number: int,
    revision_number: int,
    baseline_approval_source: str | None,
    baseline_approval: str | None,
) -> None:
    rows = connection.execute(
        """
        SELECT version_number, revision_number
        FROM communication_release_tags
        WHERE target_id = ? AND tag_kind = 'checkpoint'
        ORDER BY version_number, revision_number
        """,
        (target_id,),
    ).fetchall()
    if not rows:
        if (version_number, revision_number) != (1, 0):
            raise ResearchDbError("每个目标期刊 lineage 的首个正式稿件 tag 必须从 1.0 开始。")
        return

    last_version = int(rows[-1]["version_number"])
    last_revision = int(rows[-1]["revision_number"])
    if version_number == last_version and revision_number == last_revision + 1:
        return
    if version_number == last_version + 1 and revision_number == 0:
        if baseline_approval_source not in BASELINE_APPROVAL_SOURCES or not baseline_approval:
            raise ResearchDbError(
                "新的整数 baseline 需要本次用户明确批准或已有显式项目决定；"
                "请提供 baseline_approval_source=user|project_decision 与 baseline_approval。"
            )
        return
    raise ResearchDbError(
        "稿件版本必须连续：同一 baseline 只允许修订号 +1；新的整数 baseline 只允许 N.x → N+1.0。"
    )


def _tag_message(
    *,
    slug: str,
    journal_name: str,
    journal_code: str,
    version: str,
    workspace_path: str,
    canonical_source: str,
    release_date: str | None,
    release_evidence_source: str | None,
    release_evidence: str | None,
    baseline_approval_source: str | None,
    baseline_approval: str | None,
) -> str:
    lines = [
        f"Article: {slug}",
        f"Journal: {journal_name}",
        f"Journal code: {journal_code}",
        f"Version: {version}",
        f"Target workspace: {workspace_path}",
        f"Canonical source: {canonical_source}",
    ]
    if baseline_approval_source:
        lines.extend(
            [
                f"Baseline approval source: {baseline_approval_source}",
                f"Baseline approval: {baseline_approval}",
            ]
        )
    if release_date:
        lines.extend(
            [
                f"Public release date: {release_date}",
                f"Release evidence source: {release_evidence_source}",
                f"Release evidence: {release_evidence}",
            ]
        )
    return "\n".join(lines)


def tag_communication_release(project_root: Path, bundle: dict[str, Any]) -> dict[str, Any]:
    slug = common.slug(bundle.get("slug"))
    requested_code = common.text(bundle.get("journal_code"), required=True, field="journal_code")
    assert requested_code is not None
    version_number, revision_number, version = parse_release_version(bundle.get("version"))
    release_value = bundle.get("release_date")
    release_date = _release_date(release_value) if release_value is not None else None
    tag_kind = "release" if release_date else "checkpoint"

    baseline_approval_source = common.text(bundle.get("baseline_approval_source"))
    baseline_approval = common.text(bundle.get("baseline_approval"))
    if baseline_approval_source is not None and baseline_approval_source not in BASELINE_APPROVAL_SOURCES:
        raise ResearchDbError("baseline_approval_source 必须是 user 或 project_decision。")

    release_evidence_source = common.text(bundle.get("release_evidence_source"))
    release_evidence = common.text(bundle.get("release_evidence"))
    if tag_kind == "release":
        if release_evidence_source not in RELEASE_EVIDENCE_SOURCES or not release_evidence:
            raise ResearchDbError(
                "公开 release tag 只有在用户明确确认或可核验公开信息支持日期时才能创建；"
                "请提供 release_evidence_source=user_confirmation|public_source 与 release_evidence。"
            )
    elif release_evidence_source is not None or release_evidence is not None:
        raise ResearchDbError("普通 manuscript checkpoint 不应填写公开 release evidence。")

    _require_clean_worktree(project_root)

    if tag_kind == "checkpoint":
        # Reuse the existing Communication completion seam as the checkpoint build/source gate.
        from research_db_ops.completion.project.communication import communication_completion_readiness

        communication = communication_completion_readiness(project_root)
        relevant_blockers = [
            blocker
            for blocker in communication["blockers"]
            if blocker.get("communication") == slug
            and blocker.get("journal_code", requested_code) == requested_code
        ]
        if relevant_blockers:
            raise ResearchDbError(
                "target release workspace 尚未通过 source/build provenance gate："
                + "; ".join(str(item.get("reason")) for item in relevant_blockers)
            )

    with connect(common.db_path(project_root)) as connection:
        target = connection.execute(
            """
            SELECT tw.*, cp.slug AS product_slug, cp.canonical_source_path,
                   j.name AS journal_name, j.code AS registered_journal_code
            FROM communication_target_workspaces AS tw
            JOIN communication_products AS cp ON cp.id = tw.product_id
            JOIN communication_journals AS j ON j.code = tw.journal_code
            WHERE cp.slug = ? AND tw.journal_code = ? COLLATE NOCASE
            """,
            (slug, requested_code),
        ).fetchone()
        if target is None:
            raise ResearchDbError(
                f"目标期刊 release workspace 尚未登记：article={slug}; journal={requested_code}。"
            )
        code = str(target["registered_journal_code"])
        if code != requested_code:
            raise ResearchDbError(f"journal_code 必须使用已登记拼写 {code}。")
        target_id = int(target["id"])
        canonical_source = str(target["canonical_source_path"] or "").strip()
        workspace = str(target["workspace_path"])
        journal_name = str(target["journal_name"])

        tag_name = f"{slug}/{code}-{version}"
        if release_date:
            tag_name += "-release-" + release_date.replace("-", "")
        recorded = connection.execute(
            "SELECT 1 FROM communication_release_tags WHERE tag_name = ?",
            (tag_name,),
        ).fetchone()
        if recorded is not None or _tag_exists(project_root, tag_name):
            raise ResearchDbError(
                f"正式 manuscript tag 已存在：{tag_name}；不可移动、force 更新或删除重建来改变历史含义。"
            )

        if tag_kind == "checkpoint":
            target_source_paths = [canonical_source, ".research/research.sqlite"] + [
                str(row["path"])
                for row in connection.execute(
                    "SELECT path FROM communication_target_files WHERE target_id = ? ORDER BY id",
                    (target_id,),
                )
            ]
            _require_tracked_at_head(project_root, target_source_paths)
            _checkpoint_sequence(
                connection,
                target_id,
                version_number=version_number,
                revision_number=revision_number,
                baseline_approval_source=baseline_approval_source,
                baseline_approval=baseline_approval,
            )
            manifest = load_target_manifest(
                project_root,
                slug=slug,
                code=code,
                expected_canonical_source=canonical_source,
                expected_source_commit=str(target["source_commit"]),
            )
            verify_target_build(project_root, manifest)
            _require_clean_worktree(project_root)
            leaked_outputs = stored_generated_outputs(
                project_root,
                str(manifest["workspace_path"]),
                list(manifest["generated_outputs"]),
            )
            if leaked_outputs:
                raise ResearchDbError(
                    "target release build 把生成表示写回 source tree；formal checkpoint build 只能写入临时 output_dir："
                    + ", ".join(leaked_outputs)
                )
            commit_oid = _head_commit(project_root)
        else:
            base = connection.execute(
                """
                SELECT * FROM communication_release_tags
                WHERE target_id = ? AND version_number = ? AND revision_number = ?
                  AND tag_kind = 'checkpoint'
                """,
                (target_id, version_number, revision_number),
            ).fetchone()
            if base is None:
                raise ResearchDbError(
                    f"公开 release 必须先存在基础 manuscript checkpoint：{slug}/{code}-{version}。"
                )
            commit_oid = str(base["commit_oid"])

        message = _tag_message(
            slug=slug,
            journal_name=journal_name,
            journal_code=code,
            version=version,
            workspace_path=workspace,
            canonical_source=canonical_source,
            release_date=release_date,
            release_evidence_source=release_evidence_source,
            release_evidence=release_evidence,
            baseline_approval_source=baseline_approval_source,
            baseline_approval=baseline_approval,
        )

        connection.execute("BEGIN IMMEDIATE")
        created_tag = False
        try:
            _git(project_root, "tag", "-a", tag_name, commit_oid, "-m", message)
            created_tag = True
            tag_object_oid = _tag_object_oid(project_root, tag_name)
            if _tag_commit(project_root, tag_name) != commit_oid:
                raise ResearchDbError("新建 annotated tag 没有指向预期 commit。")
            now = common.now()
            connection.execute(
                """
                INSERT INTO communication_release_tags(
                    target_id, tag_name, version_number, revision_number, tag_kind,
                    release_date, baseline_approval_source, baseline_approval,
                    release_evidence_source, release_evidence,
                    commit_oid, tag_object_oid, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    target_id,
                    tag_name,
                    version_number,
                    revision_number,
                    tag_kind,
                    release_date,
                    baseline_approval_source,
                    baseline_approval,
                    release_evidence_source,
                    release_evidence,
                    commit_oid,
                    tag_object_oid,
                    now,
                ),
            )
            connection.execute(
                """
                INSERT INTO change_log(timestamp, action, entity_type, entity_id, reason, summary)
                VALUES (?, 'communication_release_tag_created', 'communication_target_workspace', ?, ?, ?)
                """,
                (
                    now,
                    str(target_id),
                    "Immutable annotated manuscript tag created through the supported release gate.",
                    f"tag={tag_name}; commit={commit_oid}; kind={tag_kind}",
                ),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            if created_tag:
                _git(project_root, "tag", "-d", tag_name, check=False)
            raise

    return {
        "ok": True,
        "tag": tag_name,
        "kind": tag_kind,
        "version": version,
        "commit": commit_oid,
        "tag_object_oid": tag_object_oid,
        "release_date": release_date,
    }

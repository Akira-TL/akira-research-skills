from __future__ import annotations

from typing import Any, Callable

from research_db_core import discover_project_root
from research_db_ops.project import (
    clear_tracked_artifact_checksums,
    get_research_tree,
    list_freeze_revisions,
    list_path_migrations,
    list_tracked_artifact_checksums,
    migrate_human_artifact_path,
    record_freeze_revisions,
    record_path_migration,
    list_research_branches,
    list_studies,
    record_research_branch,
    record_research_edge,
    record_research_node,
    record_study,
    redact_text_checksums,
    render_research_tree_view,
    set_research_tree_state,
)


PROJECT_BUNDLE_DEFAULTS = {
    "record-research-node": "research-node.json",
    "record-research-edge": "research-edge.json",
    "record-research-branch": "research-branch.json",
    "set-research-tree-state": "research-tree-state.json",
    "record-study": "study.json",
    "migrate-human-artifact-path": "human-artifact-path-migration.json",
    "record-freeze-revisions": "freeze-revisions.json",
    "record-path-migration": "path-migration.json",
}


def register_project_commands(
    subparsers: Any,
    *,
    emit: Callable[[dict[str, Any]], None],
    load_json: Callable[[Any, str, str | None], dict[str, Any]],
) -> None:
    def cmd_record_research_node(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(
            record_research_node(
                project_root,
                load_json(project_root, "record-research-node", args.bundle),
            )
        )
        return 0

    def cmd_record_research_edge(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(
            record_research_edge(
                project_root,
                load_json(project_root, "record-research-edge", args.bundle),
            )
        )
        return 0

    def cmd_set_research_tree_state(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(
            set_research_tree_state(
                project_root,
                load_json(project_root, "set-research-tree-state", args.bundle),
            )
        )
        return 0

    def cmd_research_tree(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(get_research_tree(project_root, limit=args.limit))
        return 0

    def cmd_render_research_tree_view(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(render_research_tree_view(project_root))
        return 0

    def cmd_research_branches(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(list_research_branches(project_root, limit=args.limit))
        return 0

    def cmd_record_research_branch(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(
            record_research_branch(
                project_root,
                load_json(project_root, "record-research-branch", args.bundle),
            )
        )
        return 0

    def cmd_migrate_human_artifact_path(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(
            migrate_human_artifact_path(
                project_root,
                load_json(project_root, "migrate-human-artifact-path", args.bundle),
            )
        )
        return 0

    def cmd_record_freeze_revisions(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(
            record_freeze_revisions(
                project_root,
                load_json(project_root, "record-freeze-revisions", args.bundle),
            )
        )
        return 0

    def cmd_freeze_revisions(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(list_freeze_revisions(project_root, pending=args.pending, limit=args.limit))
        return 0

    def cmd_record_path_migration(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(
            record_path_migration(
                project_root,
                load_json(project_root, "record-path-migration", args.bundle),
            )
        )
        return 0

    def cmd_path_migrations(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(list_path_migrations(project_root))
        return 0

    def cmd_tracked_artifact_checksums(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(list_tracked_artifact_checksums(project_root))
        return 0

    def cmd_clear_tracked_artifact_checksums(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(clear_tracked_artifact_checksums(project_root, reason=args.reason, dry_run=args.dry_run))
        return 0

    def cmd_redact_text_checksums(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(redact_text_checksums(project_root, reason=args.reason, dry_run=args.dry_run))
        return 0

    def cmd_record_study(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(
            record_study(
                project_root,
                load_json(project_root, "record-study", args.bundle),
            )
        )
        return 0

    def cmd_studies(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(list_studies(project_root, limit=args.limit))
        return 0

    for name, help_text, handler in (
        ("research-tree", "读取项目 Research Tree、active path 与科学关系。", cmd_research_tree),
        ("research-branches", "列出 Research Tree 与 Git 科研分支的绑定和归档状态。", cmd_research_branches),
        ("studies", "列出项目级 Study execution、Sample、Assay 与 deviation provenance。", cmd_studies),
    ):
        parser = subparsers.add_parser(name, help=help_text)
        parser.add_argument("--limit", type=int, default=100)
        parser.set_defaults(handler=handler)

    revisions_parser = subparsers.add_parser(
        "freeze-revisions",
        help="列出冻结对象的已登记修订说明；--pending 同时列出尚未登记的冻结后内容变化。",
    )
    revisions_parser.add_argument("--pending", action="store_true")
    revisions_parser.add_argument("--limit", type=int, default=500)
    revisions_parser.set_defaults(handler=cmd_freeze_revisions)

    migrations_parser = subparsers.add_parser(
        "path-migrations",
        help="列出已登记的整体目录迁移（迁移提交、旧前缀、新前缀）。",
    )
    migrations_parser.set_defaults(handler=cmd_path_migrations)

    checksum_parser = subparsers.add_parser(
        "tracked-artifact-checksums",
        help="只读列出 version 中仍带 SHA256 的 Git 跟踪 Dataset/Study artifact，供项目清理。",
    )
    checksum_parser.set_defaults(handler=cmd_tracked_artifact_checksums)

    clear_parser = subparsers.add_parser(
        "clear-tracked-artifact-checksums",
        help="清空 Git 跟踪 Dataset/Study artifact 的 version 中纯 SHA256 值，逐条写 change_log。",
    )
    clear_parser.add_argument("--dry-run", action="store_true")
    clear_parser.add_argument("--reason")
    clear_parser.set_defaults(handler=cmd_clear_tracked_artifact_checksums)

    redact_parser = subparsers.add_parser(
        "redact-text-checksums",
        help="把说明/理由/摘要类自由文本中的独立 SHA256 替换为固定占位文本，逐格写 change_log；--dry-run 只列出。",
    )
    redact_parser.add_argument("--dry-run", action="store_true")
    redact_parser.add_argument("--reason")
    redact_parser.set_defaults(handler=cmd_redact_text_checksums)

    render_parser = subparsers.add_parser(
        "render-research-tree-view",
        help="从 canonical Research Tree 生成完整 research-tree/README.md 人类视图。",
    )
    render_parser.set_defaults(handler=cmd_render_research_tree_view)

    for name, help_text, bundle_help, handler in (
        (
            "record-research-node",
            "登记或更新一个 Research Tree scientific node 的 workflow state。",
            "Research Node JSON bundle；默认 .research/bundles/research-node.json；传 '-' 从 stdin 读取。",
            cmd_record_research_node,
        ),
        (
            "record-research-edge",
            "登记主模型已核验的 Research Tree 科学关系及其 evidence basis。",
            "Research Edge JSON bundle；默认 .research/bundles/research-edge.json；传 '-' 从 stdin 读取。",
            cmd_record_research_edge,
        ),
        (
            "record-research-branch",
            "登记 Research Node 对应的 canonical Git 科研分支，以及 merged/archived 收口状态。",
            "Research Branch JSON bundle；默认 .research/bundles/research-branch.json；传 '-' 从 stdin 读取。",
            cmd_record_research_branch,
        ),
        (
            "set-research-tree-state",
            "设置 Root 与 primary active Research Node，并校验 active path。",
            "Research Tree State JSON bundle；默认 .research/bundles/research-tree-state.json；传 '-' 从 stdin 读取。",
            cmd_set_research_tree_state,
        ),
        (
            "record-study",
            "登记真实 Study execution、Sample、Assay、deviation 与 artifact provenance。",
            "Study JSON bundle；默认 .research/bundles/study.json；传 '-' 从 stdin 读取。",
            cmd_record_study,
        ),
        (
            "record-freeze-revisions",
            "批量登记冻结对象在冻结提交之后的修订说明（路径、修订提交、类别、原因）。",
            "Freeze revisions JSON bundle；默认 .research/bundles/freeze-revisions.json；传 '-' 从 stdin 读取。",
            cmd_record_freeze_revisions,
        ),
        (
            "record-path-migration",
            "登记整体目录迁移，并一次性把数据库全部路径字段改写到迁移后的位置。",
            "Path migration JSON bundle；默认 .research/bundles/path-migration.json；传 '-' 从 stdin 读取。",
            cmd_record_path_migration,
        ),
        (
            "migrate-human-artifact-path",
            "仅迁移既有 Dataset/Analysis 的 canonical human artifact 路径，不改科学身份或结果字段。",
            "Human artifact path migration JSON bundle；默认 .research/bundles/human-artifact-path-migration.json；传 '-' 从 stdin 读取。",
            cmd_migrate_human_artifact_path,
        ),
    ):
        parser = subparsers.add_parser(name, help=help_text)
        parser.add_argument("bundle", nargs="?", help=bundle_help)
        parser.set_defaults(handler=handler)

from __future__ import annotations

from typing import Any, Callable

from research_db_core import discover_project_root
from research_db_ops.communication import (
    list_communications,
    record_communication,
    record_journal,
    record_target_workspace,
    relocate_communication_artifact,
    tag_communication_release,
)


COMMUNICATION_BUNDLE_DEFAULTS = {
    "record-communication": "communication.json",
    "record-journal": "communication-journal.json",
    "record-target-workspace": "communication-target-workspace.json",
    "tag-communication-release": "communication-release-tag.json",
    "relocate-communication-artifact": "communication-artifact-relocation.json",
}


def register_communication_commands(
    subparsers: Any,
    *,
    emit: Callable[[dict[str, Any]], None],
    load_json: Callable[[Any, str, str | None], dict[str, Any]],
) -> None:
    def cmd_record_communication(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(
            record_communication(
                project_root,
                load_json(project_root, "record-communication", args.bundle),
            )
        )
        return 0

    def cmd_record_journal(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(
            record_journal(
                project_root,
                load_json(project_root, "record-journal", args.bundle),
            )
        )
        return 0

    def cmd_record_target_workspace(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(
            record_target_workspace(
                project_root,
                load_json(project_root, "record-target-workspace", args.bundle),
            )
        )
        return 0

    def cmd_tag_communication_release(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(
            tag_communication_release(
                project_root,
                load_json(project_root, "tag-communication-release", args.bundle),
            )
        )
        return 0

    def cmd_relocate_communication_artifact(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(
            relocate_communication_artifact(
                project_root,
                load_json(project_root, "relocate-communication-artifact", args.bundle),
            )
        )
        return 0

    def cmd_communications(args: Any) -> int:
        project_root = discover_project_root(args.project)
        emit(list_communications(project_root, limit=args.limit))
        return 0

    list_parser = subparsers.add_parser(
        "communications",
        help="列出项目级 Communication Product provenance。",
    )
    list_parser.add_argument("--limit", type=int, default=100)
    list_parser.set_defaults(handler=cmd_communications)

    for name, help_text, bundle_help, handler in (
        (
            "record-communication",
            "登记传播产物、pre-communication source commit、canonical editable source 与派生 artifact provenance。",
            "Communication JSON bundle；默认 .research/bundles/communication.json；传 '-' 从 stdin 读取。",
            cmd_record_communication,
        ),
        (
            "record-journal",
            "登记或刷新项目内稳定 target journal code；同一期刊不能创建多个临时代码。",
            "Journal registry JSON bundle；默认 .research/bundles/communication-journal.json；传 '-' 从 stdin 读取。",
            cmd_record_journal,
        ),
        (
            "record-target-workspace",
            "登记 <journal-code>-release target build workspace，并绑定共享 canonical communication source。",
            "Target workspace JSON bundle；默认 .research/bundles/communication-target-workspace.json；传 '-' 从 stdin 读取。",
            cmd_record_target_workspace,
        ),
        (
            "tag-communication-release",
            "通过唯一受支持的 release gate 创建不可变 annotated manuscript checkpoint/public release tag。",
            "Communication release tag JSON bundle；默认 .research/bundles/communication-release-tag.json；传 '-' 从 stdin 读取。",
            cmd_tag_communication_release,
        ),
        (
            "relocate-communication-artifact",
            "在文件系统迁移完成后，受控更新 Communication artifact 的 provenance 路径。",
            "Communication artifact relocation JSON bundle；默认 .research/bundles/communication-artifact-relocation.json；传 '-' 从 stdin 读取。",
            cmd_relocate_communication_artifact,
        ),
    ):
        parser = subparsers.add_parser(name, help=help_text)
        parser.add_argument("bundle", nargs="?", help=bundle_help)
        parser.set_defaults(handler=handler)

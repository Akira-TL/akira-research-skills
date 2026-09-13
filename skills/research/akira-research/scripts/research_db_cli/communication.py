from __future__ import annotations

from typing import Any, Callable

from research_db_core import discover_project_root
from research_db_ops.communication import (
    list_communications,
    record_communication,
    relocate_communication_artifact,
)


COMMUNICATION_BUNDLE_DEFAULTS = {
    "record-communication": "communication.json",
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
            "登记传播产物、pre-communication source commit 与派生 artifact provenance。",
            "Communication JSON bundle；默认 .research/bundles/communication.json；传 '-' 从 stdin 读取。",
            cmd_record_communication,
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

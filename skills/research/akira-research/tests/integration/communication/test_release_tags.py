from __future__ import annotations

from contextlib import closing
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from research_db_core import init_database  # noqa: E402
from research_db_ops.communication import (  # noqa: E402
    record_communication,
    record_journal,
    record_target_workspace,
    tag_communication_release,
)
from research_db_ops.completion import validate_completion  # noqa: E402
from research_db_support.storage import ResearchDbError  # noqa: E402


RESEARCH_MD = """# Research

## Objective

验证稿件 Git 版本锚点与目标期刊工作区保持一致。

## Applicable Standards

不适用：当前没有额外正式规范。

## Current Loop

COMMUNICATION

## Active Uncertainty

正式稿件版本锚点是否保持不可变并对应真实目标工作区？

## Current State

当前科学证据和目标期刊工作区已经稳定，可以形成正式稿件 checkpoint。

## Active Work

建立不可变稿件版本 tag，并保持公开 release 与基础版本内容一致。

## Open Threads

暂无其他优先传播问题。

## Key Decisions

稿件版本采用版本号与修订号，不使用 final 或 latest 表述。

## Navigation

不适用：当前没有其他人类可读科研入口。

## References

- `.research/research.sqlite`
"""


class CommunicationReleaseTagTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "RESEARCH.md").write_text(RESEARCH_MD, encoding="utf-8")
        init_database(self.root)
        subprocess.run(["git", "init", str(self.root)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.email", "research@example.test"], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.name", "Research Test"], check=True)
        self._prepare_article()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _commit(self, message: str) -> str:
        subprocess.run(["git", "-C", str(self.root), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-m", message], check=True, capture_output=True)
        return subprocess.run(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()

    def _prepare_article(self) -> None:
        scientific_source = self._commit("RESEARCH: freeze scientific source")
        manuscript = self.root / "communication" / "yak-ecology" / "manuscript.md"
        manuscript.parent.mkdir(parents=True)
        manuscript.write_text("# 牦牛生态对应关系\n\n不绑定目标期刊的规范传播源。\n", encoding="utf-8")
        record_communication(
            self.root,
            {
                "slug": "yak-ecology",
                "title": "牦牛生态对应关系",
                "purpose": "形成论文规范传播源",
                "audience": "科研读者",
                "source_commit": scientific_source,
                "canonical_source_path": "communication/yak-ecology/manuscript.md",
                "status": "draft",
                "artifacts": [
                    {
                        "role": "other",
                        "path": "communication/yak-ecology/manuscript.md",
                        "timing_role": "derived_output",
                    }
                ],
            },
        )
        manuscript_commit = self._commit("DOCS: add canonical manuscript")
        self._prepare_target("NC", "Nature Communications", manuscript_commit)

    def _prepare_target(self, code: str, name: str, source_commit: str | None = None) -> None:
        source_commit = source_commit or subprocess.run(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
        record_journal(
            self.root,
            {
                "code": code,
                "name": name,
                "official_source": f"https://example.test/{code}",
                "checked_at": "2026-09-13T00:00:00+00:00",
            },
        )
        workspace = self.root / "communication" / "yak-ecology" / f"{code}-release"
        workspace.mkdir(parents=True, exist_ok=True)
        (workspace / "build.py").write_text(
            """from __future__ import annotations

import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output-dir", required=True)
args = parser.parse_args()
output_dir = Path(args.output_dir)
output_dir.mkdir(parents=True, exist_ok=True)
for name in ("manuscript.docx", "manuscript.pdf"):
    (output_dir / name).write_bytes(b"deterministic release output")
""",
            encoding="utf-8",
        )
        (workspace / "journal.json").write_text(json.dumps({"journal_code": code}) + "\n", encoding="utf-8")
        (workspace / "QA.md").write_text("# QA\n\n已核对 target build source 与页面验收要求。\n", encoding="utf-8")
        (workspace / "manifest.json").write_text(
            json.dumps(
                {
                    "journal_code": code,
                    "canonical_source": "communication/yak-ecology/manuscript.md",
                    "source_commit": source_commit,
                    "config": "journal.json",
                    "build_sources": ["build.py"],
                    "build_command": [sys.executable, "build.py", "--output-dir", "{output_dir}"],
                    "template_status": "not_provided",
                    "templates": [],
                    "qa_evidence": ["QA.md"],
                    "generated_outputs": ["manuscript.docx", "manuscript.pdf"],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        record_target_workspace(
            self.root,
            {"slug": "yak-ecology", "journal_code": code, "source_commit": source_commit},
        )
        self._commit(f"BUILD: prepare {code} target workspace")

    def _checkpoint(self, version: str, **extra: object) -> dict[str, object]:
        payload: dict[str, object] = {
            "slug": "yak-ecology",
            "journal_code": "NC",
            "version": version,
        }
        payload.update(extra)
        result = tag_communication_release(self.root, payload)
        self._commit(f"RESEARCH: record NC {version} tag provenance")
        return result

    def test_first_checkpoint_is_annotated_1_0(self) -> None:
        result = self._checkpoint("1.0")

        self.assertEqual(result["tag"], "yak-ecology/NC-1.0")
        self.assertEqual(
            subprocess.run(
                ["git", "-C", str(self.root), "cat-file", "-t", "refs/tags/yak-ecology/NC-1.0"],
                check=True,
                text=True,
                capture_output=True,
            ).stdout.strip(),
            "tag",
        )
        self.assertTrue(validate_completion(self.root)["communication"]["ready"])
        workspace = self.root / "communication" / "yak-ecology" / "NC-release"
        self.assertFalse((workspace / "manuscript.docx").exists())
        self.assertFalse((workspace / "manuscript.pdf").exists())

    def test_checkpoint_rejects_non_reproducible_target_build(self) -> None:
        workspace = self.root / "communication" / "yak-ecology" / "NC-release"
        (workspace / "build.py").write_text(
            """from __future__ import annotations

import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output-dir", required=True)
args = parser.parse_args()
output_dir = Path(args.output_dir)
output_dir.mkdir(parents=True, exist_ok=True)
(output_dir / "manuscript.docx").write_bytes(b"incomplete output")
""",
            encoding="utf-8",
        )
        self._commit("BUILD: make target build incomplete")
        with closing(sqlite3.connect(self.root / ".research" / "research.sqlite")) as connection:
            source_commit = connection.execute(
                "SELECT source_commit FROM communication_target_workspaces WHERE journal_code = 'NC'"
            ).fetchone()[0]
        record_target_workspace(
            self.root,
            {"slug": "yak-ecology", "journal_code": "NC", "source_commit": source_commit},
        )
        self._commit("RESEARCH: refresh target build provenance")

        with self.assertRaisesRegex(ResearchDbError, "没有生成.*manuscript.pdf"):
            tag_communication_release(
                self.root,
                {"slug": "yak-ecology", "journal_code": "NC", "version": "1.0"},
            )

        self.assertFalse(
            subprocess.run(
                ["git", "-C", str(self.root), "show-ref", "--verify", "--quiet", "refs/tags/yak-ecology/NC-1.0"],
                check=False,
            ).returncode
            == 0
        )

    def test_revision_sequence_is_contiguous_and_not_semver(self) -> None:
        self._checkpoint("1.0")
        self._checkpoint("1.1")
        with self.assertRaisesRegex(ResearchDbError, "连续"):
            self._checkpoint("1.3")
        with self.assertRaisesRegex(ResearchDbError, "版本号.修订号"):
            self._checkpoint("1.1.1")
        with self.assertRaisesRegex(ResearchDbError, "版本号.修订号"):
            self._checkpoint("v1.2")

    def test_new_integer_baseline_requires_explicit_approval(self) -> None:
        self._checkpoint("1.0")
        self._checkpoint("1.1")
        with self.assertRaisesRegex(ResearchDbError, "整数 baseline"):
            self._checkpoint("2.0")

        result = self._checkpoint(
            "2.0",
            baseline_approval_source="user",
            baseline_approval="用户确认该稿件形成新的正式版本基线。",
        )
        self.assertEqual(result["tag"], "yak-ecology/NC-2.0")

    def test_completion_rejects_missing_integer_baseline_approval_after_db_tamper(self) -> None:
        self._checkpoint("1.0")
        self._checkpoint(
            "2.0",
            baseline_approval_source="user",
            baseline_approval="用户确认新的正式版本基线。",
        )
        with closing(sqlite3.connect(self.root / ".research" / "research.sqlite")) as connection, connection:
            connection.execute(
                """
                UPDATE communication_release_tags
                SET baseline_approval_source = NULL, baseline_approval = NULL
                WHERE version_number = 2 AND revision_number = 0 AND tag_kind = 'checkpoint'
                """
            )

        result = validate_completion(self.root)

        reasons = {item["reason"] for item in result["communication"]["blockers"]}
        self.assertIn("communication_release_baseline_approval_missing", reasons)

    def test_each_journal_has_independent_1_0_lineage(self) -> None:
        self._checkpoint("1.0")
        manuscript_commit = subprocess.run(
            ["git", "-C", str(self.root), "rev-list", "--max-count=1", "--all", "--", "communication/yak-ecology/manuscript.md"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
        self._prepare_target("iMeta", "iMeta", manuscript_commit)
        result = tag_communication_release(
            self.root,
            {"slug": "yak-ecology", "journal_code": "iMeta", "version": "1.0"},
        )
        self.assertEqual(result["tag"], "yak-ecology/iMeta-1.0")

    def test_checkpoint_rejects_build_that_mutates_source_tree(self) -> None:
        workspace = self.root / "communication" / "yak-ecology" / "NC-release"
        (workspace / "build.py").write_text(
            """from __future__ import annotations

import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output-dir", required=True)
args = parser.parse_args()
output_dir = Path(args.output_dir)
output_dir.mkdir(parents=True, exist_ok=True)
for name in ("manuscript.docx", "manuscript.pdf"):
    (output_dir / name).write_bytes(b"valid temporary output")
Path("leak.txt").write_text("unexpected source-tree side effect", encoding="utf-8")
""",
            encoding="utf-8",
        )
        self._commit("BUILD: introduce source-tree side effect")
        with closing(sqlite3.connect(self.root / ".research" / "research.sqlite")) as connection:
            source_commit = connection.execute(
                "SELECT source_commit FROM communication_target_workspaces WHERE journal_code = 'NC'"
            ).fetchone()[0]
        record_target_workspace(
            self.root,
            {"slug": "yak-ecology", "journal_code": "NC", "source_commit": source_commit},
        )
        self._commit("RESEARCH: refresh target build provenance")

        with self.assertRaisesRegex(ResearchDbError, "工作树必须 clean"):
            tag_communication_release(
                self.root,
                {"slug": "yak-ecology", "journal_code": "NC", "version": "1.0"},
            )
        self.assertNotEqual(
            subprocess.run(
                ["git", "-C", str(self.root), "show-ref", "--verify", "--quiet", "refs/tags/yak-ecology/NC-1.0"],
                check=False,
            ).returncode,
            0,
        )

    def test_public_release_requires_evidence_and_points_to_base_commit(self) -> None:
        checkpoint = self._checkpoint("1.0")
        with self.assertRaisesRegex(ResearchDbError, "公开 release"):
            tag_communication_release(
                self.root,
                {
                    "slug": "yak-ecology",
                    "journal_code": "NC",
                    "version": "1.0",
                    "release_date": "2026-09-13",
                },
            )

        release = tag_communication_release(
            self.root,
            {
                "slug": "yak-ecology",
                "journal_code": "NC",
                "version": "1.0",
                "release_date": "2026-09-13",
                "release_evidence_source": "user_confirmation",
                "release_evidence": "用户明确确认论文已于该日公开。",
            },
        )
        self.assertEqual(release["tag"], "yak-ecology/NC-1.0-release-20260913")
        self.assertEqual(release["commit"], checkpoint["commit"])

    def test_public_release_rejects_future_date(self) -> None:
        self._checkpoint("1.0")
        with self.assertRaisesRegex(ResearchDbError, "未来"):
            tag_communication_release(
                self.root,
                {
                    "slug": "yak-ecology",
                    "journal_code": "NC",
                    "version": "1.0",
                    "release_date": "2099-01-01",
                    "release_evidence_source": "public_source",
                    "release_evidence": "https://example.test/publication",
                },
            )

    def test_duplicate_tag_is_never_moved_or_reused(self) -> None:
        self._checkpoint("1.0")
        with self.assertRaisesRegex(ResearchDbError, "已存在"):
            tag_communication_release(
                self.root,
                {"slug": "yak-ecology", "journal_code": "NC", "version": "1.0"},
            )

    def test_completion_detects_recreated_lightweight_tag(self) -> None:
        checkpoint = self._checkpoint("1.0")
        subprocess.run(["git", "-C", str(self.root), "tag", "-d", checkpoint["tag"]], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.root), "tag", checkpoint["tag"], checkpoint["commit"]], check=True)

        result = validate_completion(self.root)

        self.assertFalse(result["communication"]["ready"])
        reasons = {item["reason"] for item in result["communication"]["blockers"]}
        self.assertTrue(
            {"communication_release_tag_not_annotated", "communication_release_tag_object_changed"} & reasons
        )

    def test_completion_detects_moved_annotated_tag(self) -> None:
        checkpoint = self._checkpoint("1.0")
        moved_commit = subprocess.run(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
        self.assertNotEqual(moved_commit, checkpoint["commit"])
        subprocess.run(["git", "-C", str(self.root), "tag", "-d", checkpoint["tag"]], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", str(self.root), "tag", "-a", checkpoint["tag"], moved_commit, "-m", "illegally moved"],
            check=True,
        )

        result = validate_completion(self.root)

        reasons = {item["reason"] for item in result["communication"]["blockers"]}
        self.assertIn("communication_release_tag_object_changed", reasons)
        self.assertIn("communication_release_tag_commit_changed", reasons)

    def test_completion_rejects_manual_illegal_or_unregistered_article_tags(self) -> None:
        self._checkpoint("1.0")
        head = subprocess.run(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
        subprocess.run(["git", "-C", str(self.root), "tag", "yak-ecology/NC-final", head], check=True)
        subprocess.run(["git", "-C", str(self.root), "tag", "yak-ecology/NC-1.1", head], check=True)

        result = validate_completion(self.root)

        reasons = {item["reason"] for item in result["communication"]["blockers"]}
        self.assertIn("communication_release_tag_name_invalid", reasons)
        self.assertIn("communication_release_tag_unregistered", reasons)


if __name__ == "__main__":
    unittest.main()

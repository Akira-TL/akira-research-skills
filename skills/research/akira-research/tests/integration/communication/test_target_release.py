from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from research_db_core import init_database  # noqa: E402
from research_db_ops.communication import (  # noqa: E402
    list_communications,
    record_communication,
    record_journal,
    record_target_workspace,
)
from research_db_ops.completion import validate_completion  # noqa: E402
from research_db_support.storage import ResearchDbError  # noqa: E402


VALID_RESEARCH_MD = """# Research

## Objective

验证传播源与目标期刊发布工作区保持单一可编辑内容来源。

## Applicable Standards

不适用：当前没有额外正式规范。

## Current Loop

COMMUNICATION

## Active Uncertainty

目标期刊转换是否仍然来自同一份规范传播源？

## Current State

当前科学证据已经稳定，可以先形成不绑定期刊的传播草稿。

## Active Work

维护规范传播源，并在真实投稿准备时派生目标期刊工作区。

## Open Threads

暂无其他优先传播问题。

## Key Decisions

目标期刊格式不得成为第二份可独立编辑的科学稿件。

## Navigation

不适用：当前没有其他人类可读科研入口。

## References

- `.research/research.sqlite`
"""


class CommunicationTargetReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "RESEARCH.md").write_text(VALID_RESEARCH_MD, encoding="utf-8")
        init_database(self.root)
        subprocess.run(["git", "init", str(self.root)], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", str(self.root), "config", "user.email", "research@example.test"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.root), "config", "user.name", "Research Test"],
            check=True,
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _commit(self, message: str) -> str:
        subprocess.run(["git", "-C", str(self.root), "add", "-A"], check=True)
        subprocess.run(
            ["git", "-C", str(self.root), "commit", "-m", message],
            check=True,
            capture_output=True,
        )
        return subprocess.run(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()

    def _record_article(self) -> str:
        scientific_source_commit = self._commit("RESEARCH: freeze scientific source")
        manuscript = self.root / "communication" / "yak-ecology" / "manuscript.md"
        manuscript.parent.mkdir(parents=True)
        manuscript.write_text(
            "# 牦牛生态对应关系\n\n这是不绑定目标期刊的规范传播源。\n",
            encoding="utf-8",
        )
        record_communication(
            self.root,
            {
                "slug": "yak-ecology",
                "title": "牦牛生态对应关系",
                "purpose": "形成不绑定目标期刊的论文传播源",
                "audience": "科研读者",
                "source_commit": scientific_source_commit,
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
        return self._commit("DOCS: add venue-neutral manuscript source")

    def _register_journal(self, code: str = "NC", name: str = "Nature Communications") -> None:
        record_journal(
            self.root,
            {
                "code": code,
                "name": name,
                "official_source": "https://www.nature.com/ncomms/",
                "checked_at": "2026-09-13T00:00:00+00:00",
            },
        )

    def _write_target_workspace(self, code: str, source_commit: str) -> Path:
        workspace = self.root / "communication" / "yak-ecology" / f"{code}-release"
        workspace.mkdir(parents=True)
        (workspace / "build.py").write_text(
            """from __future__ import annotations

import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output-dir", required=True)
args = parser.parse_args()
output_dir = Path(args.output_dir)
output_dir.mkdir(parents=True, exist_ok=True)
for name in ("manuscript.tex", "manuscript.docx", "source-data.xlsx"):
    (output_dir / name).write_bytes(b"deterministic test output")
""",
            encoding="utf-8",
        )
        (workspace / "journal.json").write_text(
            json.dumps({"journal_code": code}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (workspace / "template.tex").write_text("% journal template source\n", encoding="utf-8")
        (workspace / "QA.md").write_text(
            "# QA\n\n当前目标格式需要实际 build 后逐页检查。\n",
            encoding="utf-8",
        )
        manifest = {
            "journal_code": code,
            "canonical_source": "communication/yak-ecology/manuscript.md",
            "source_commit": source_commit,
            "config": "journal.json",
            "build_sources": ["build.py"],
            "build_command": [sys.executable, "build.py", "--output-dir", "{output_dir}"],
            "template_status": "provided",
            "templates": ["template.tex"],
            "qa_evidence": ["QA.md"],
            "generated_outputs": ["manuscript.tex", "manuscript.docx", "source-data.xlsx"],
        }
        (workspace / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return workspace

    def _register_target(self, code: str, source_commit: str) -> None:
        record_target_workspace(
            self.root,
            {
                "slug": "yak-ecology",
                "journal_code": code,
                "source_commit": source_commit,
            },
        )

    def test_venue_neutral_draft_needs_no_journal(self) -> None:
        self._record_article()

        result = validate_completion(self.root)

        self.assertTrue(result["communication"]["ready"], result["communication"]["blockers"])
        product = list_communications(self.root)["communications"][0]
        self.assertEqual(product["canonical_source_path"], "communication/yak-ecology/manuscript.md")
        self.assertEqual(product["target_workspaces"], [])

    def test_journal_code_is_stable_and_same_journal_cannot_gain_alias(self) -> None:
        self._register_journal()
        self._register_journal()

        with self.assertRaisesRegex(ResearchDbError, "期刊.*已经登记.*NC"):
            self._register_journal(code="NComms", name="Nature Communications")
        with self.assertRaisesRegex(ResearchDbError, "期刊代码.*NC"):
            self._register_journal(code="NC", name="Nature Climate Change")

    def test_target_workspace_uses_registered_code_and_shared_canonical_source(self) -> None:
        source_commit = self._record_article()
        self._register_journal("NC", "Nature Communications")
        self._write_target_workspace("NC", source_commit)
        self._register_target("NC", source_commit)
        self._commit("BUILD: prepare NC target release source")

        result = validate_completion(self.root)

        self.assertTrue(result["communication"]["ready"], result["communication"]["blockers"])
        product = list_communications(self.root)["communications"][0]
        target = product["target_workspaces"][0]
        self.assertEqual(target["journal_code"], "NC")
        self.assertEqual(target["workspace_path"], "communication/yak-ecology/NC-release")
        self.assertEqual(target["canonical_source_path"], product["canonical_source_path"])

    def test_one_article_can_target_multiple_journals_without_copying_manuscript(self) -> None:
        source_commit = self._record_article()
        self._register_journal("NC", "Nature Communications")
        self._write_target_workspace("NC", source_commit)
        self._register_target("NC", source_commit)
        self._register_journal("iMeta", "iMeta")
        self._write_target_workspace("iMeta", source_commit)
        self._register_target("iMeta", source_commit)
        self._commit("BUILD: prepare two journal targets")

        product = list_communications(self.root)["communications"][0]
        self.assertEqual(
            [target["journal_code"] for target in product["target_workspaces"]],
            ["NC", "iMeta"],
        )
        self.assertTrue(
            all(
                target["canonical_source_path"] == "communication/yak-ecology/manuscript.md"
                for target in product["target_workspaces"]
            )
        )

    def test_canonical_source_cannot_live_inside_target_release_workspace(self) -> None:
        scientific_source_commit = self._commit("RESEARCH: freeze source")
        source = self.root / "communication" / "yak-ecology" / "NC-release" / "manuscript.md"
        source.parent.mkdir(parents=True)
        source.write_text("# 错误来源\n", encoding="utf-8")

        with self.assertRaisesRegex(ResearchDbError, "canonical.*release"):
            record_communication(
                self.root,
                {
                    "slug": "yak-ecology",
                    "title": "牦牛生态对应关系",
                    "purpose": "测试错误来源",
                    "audience": "科研读者",
                    "source_commit": scientific_source_commit,
                    "canonical_source_path": "communication/yak-ecology/NC-release/manuscript.md",
                    "artifacts": [
                        {
                            "role": "other",
                            "path": "communication/yak-ecology/NC-release/manuscript.md",
                        }
                    ],
                },
            )

    def test_target_workspace_rejects_generated_compound_files_in_git_source_tree(self) -> None:
        source_commit = self._record_article()
        self._register_journal()
        workspace = self._write_target_workspace("NC", source_commit)
        self._register_target("NC", source_commit)
        (workspace / "manuscript.docx").write_bytes(b"generated output")
        self._commit("BUILD: accidentally store generated docx")

        result = validate_completion(self.root)
        reasons = {item["reason"] for item in result["communication"]["blockers"]}

        self.assertIn("communication_target_generated_output_stored", reasons)

    def test_target_workspace_rejects_manifest_declared_generated_latex(self) -> None:
        source_commit = self._record_article()
        self._register_journal()
        workspace = self._write_target_workspace("NC", source_commit)
        self._register_target("NC", source_commit)
        (workspace / "manuscript.tex").write_text(
            "% generated target representation; do not edit here\n",
            encoding="utf-8",
        )
        self._commit("BUILD: accidentally store generated latex")

        result = validate_completion(self.root)
        blockers = result["communication"]["blockers"]

        blocker = next(
            item
            for item in blockers
            if item["reason"] == "communication_target_generated_output_stored"
        )
        self.assertIn(
            "communication/yak-ecology/NC-release/manuscript.tex",
            blocker["paths"],
        )

    def test_target_workspace_becomes_stale_when_build_source_changes(self) -> None:
        source_commit = self._record_article()
        self._register_journal()
        workspace = self._write_target_workspace("NC", source_commit)
        self._register_target("NC", source_commit)
        self._commit("BUILD: prepare NC target")
        (workspace / "build.py").write_text(
            "# revised target-specific build entrypoint\n",
            encoding="utf-8",
        )
        self._commit("BUILD: revise NC build source")

        result = validate_completion(self.root)
        reasons = {item["reason"] for item in result["communication"]["blockers"]}

        self.assertIn("communication_target_build_source_drift", reasons)

    def test_release_named_workspace_requires_target_registry(self) -> None:
        self._record_article()
        release_dir = self.root / "communication" / "yak-ecology" / "NC-release"
        release_dir.mkdir()
        (release_dir / "build.py").write_text("# undeclared target build\n", encoding="utf-8")
        self._commit("BUILD: add undeclared target release workspace")

        result = validate_completion(self.root)
        reasons = {item["reason"] for item in result["communication"]["blockers"]}

        self.assertIn("communication_target_workspace_unregistered", reasons)

    def test_target_workspace_rejects_second_editable_manuscript_even_if_registered(self) -> None:
        source_commit = self._record_article()
        self._register_journal()
        workspace = self._write_target_workspace("NC", source_commit)
        self._register_target("NC", source_commit)
        duplicate = workspace / "manuscript-copy.md"
        duplicate.write_text("# 第二份稿件\n\n这不应成为独立内容来源。\n", encoding="utf-8")
        product = list_communications(self.root)["communications"][0]
        record_communication(
            self.root,
            {
                "slug": "yak-ecology",
                "title": product["title"],
                "purpose": product["purpose"],
                "audience": product["audience"],
                "source_commit": product["source_commit"],
                "status": product["status"],
                "artifacts": [
                    {
                        "role": "other",
                        "path": "communication/yak-ecology/NC-release/manuscript-copy.md",
                        "timing_role": "derived_output",
                    }
                ],
            },
        )
        self._commit("DOCS: register duplicate target manuscript")

        result = validate_completion(self.root)
        blockers = result["communication"]["blockers"]

        blocker = next(
            item
            for item in blockers
            if item["reason"] == "communication_target_unexpected_file"
        )
        self.assertEqual(
            blocker["paths"],
            ["communication/yak-ecology/NC-release/manuscript-copy.md"],
        )

    def test_target_workspace_becomes_stale_when_canonical_source_changes(self) -> None:
        source_commit = self._record_article()
        self._register_journal()
        self._write_target_workspace("NC", source_commit)
        self._register_target("NC", source_commit)
        self._commit("BUILD: prepare NC target")
        manuscript = self.root / "communication" / "yak-ecology" / "manuscript.md"
        manuscript.write_text(
            manuscript.read_text(encoding="utf-8") + "\n新增一段规范稿件内容。\n",
            encoding="utf-8",
        )
        self._commit("DOCS: revise canonical manuscript")

        result = validate_completion(self.root)
        reasons = {item["reason"] for item in result["communication"]["blockers"]}

        self.assertIn("communication_target_source_drift", reasons)

    def test_target_manifest_identity_must_match_registry_and_product(self) -> None:
        source_commit = self._record_article()
        self._register_journal()
        workspace = self._write_target_workspace("NC", source_commit)
        manifest_path = workspace / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["journal_code"] = "iMeta"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        with self.assertRaisesRegex(ResearchDbError, "manifest.*journal_code"):
            self._register_target("NC", source_commit)


if __name__ == "__main__":
    unittest.main()

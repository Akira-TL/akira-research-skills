from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from research_db_ops.completion import project_state_readiness  # noqa: E402


VALID_RESEARCH_MD = """# Research

## Objective

验证人类可读科研状态格式。

## Applicable Standards

不适用：当前没有额外正式规范。

## Current Loop

QUESTION

## Active Uncertainty

当前最需要区分的科学解释是什么？

## Current State

当前证据状态已记录。

## Active Work

等待下一条能够区分竞争解释的证据。

## Open Threads

暂无当前优先处理的其他问题。

## Key Decisions

保持当前证据边界。

## Navigation

暂无其他科研入口。

## References

- `.research/research.sqlite`
"""


class HumanArtifactContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "RESEARCH.md").write_text(VALID_RESEARCH_MD, encoding="utf-8")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_research_state_requires_unique_h1(self) -> None:
        (self.root / "RESEARCH.md").write_text(
            VALID_RESEARCH_MD + "\n# Duplicate Research\n",
            encoding="utf-8",
        )

        result = project_state_readiness(self.root)

        self.assertFalse(result["ready"])
        blocker = next(
            item for item in result["blockers"] if item["reason"] == "human_markdown_h1_invalid"
        )
        self.assertEqual(blocker["count"], 2)

    def test_research_state_rejects_versioned_format_marker(self) -> None:
        invalid = VALID_RESEARCH_MD.replace(
            "# Research\n",
            "# Research\n\n<!-- akira:research-state:v1 -->\n",
            1,
        )
        (self.root / "RESEARCH.md").write_text(invalid, encoding="utf-8")

        result = project_state_readiness(self.root)

        self.assertFalse(result["ready"])
        self.assertTrue(
            any(item["reason"] == "human_markdown_versioned_marker" for item in result["blockers"])
        )

    def test_research_state_requires_exact_h2_order(self) -> None:
        reordered = VALID_RESEARCH_MD.replace(
            "## Objective\n\n验证人类可读科研状态格式。\n\n## Applicable Standards\n\n不适用：当前没有额外正式规范。",
            "## Applicable Standards\n\n不适用：当前没有额外正式规范。\n\n## Objective\n\n验证人类可读科研状态格式。",
            1,
        )
        (self.root / "RESEARCH.md").write_text(reordered, encoding="utf-8")

        result = project_state_readiness(self.root)

        self.assertFalse(result["ready"])
        self.assertTrue(
            any(item["reason"] == "human_markdown_section_order_invalid" for item in result["blockers"])
        )

    def test_research_state_rejects_empty_required_section(self) -> None:
        invalid = VALID_RESEARCH_MD.replace(
            "## Current State\n\n当前证据状态已记录。",
            "## Current State\n",
            1,
        )
        (self.root / "RESEARCH.md").write_text(invalid, encoding="utf-8")

        result = project_state_readiness(self.root)

        self.assertFalse(result["ready"])
        blocker = next(
            item for item in result["blockers"] if item["reason"] == "human_markdown_empty_sections"
        )
        self.assertEqual(blocker["sections"], ["Current State"])

    def test_research_state_rejects_broken_human_link(self) -> None:
        invalid = VALID_RESEARCH_MD.replace(
            "暂无其他科研入口。",
            "- [假设索引](hypotheses/README.md)",
            1,
        )
        (self.root / "RESEARCH.md").write_text(invalid, encoding="utf-8")

        result = project_state_readiness(self.root)

        self.assertFalse(result["ready"])
        blocker = next(
            item for item in result["blockers"] if item["reason"] == "human_markdown_link_missing"
        )
        self.assertEqual(blocker["target"], "hypotheses/README.md")

    def test_research_state_rejects_machine_internal_human_link(self) -> None:
        invalid = VALID_RESEARCH_MD.replace(
            "暂无其他科研入口。",
            "- [数据库](.research/research.sqlite)",
            1,
        )
        (self.root / "RESEARCH.md").write_text(invalid, encoding="utf-8")

        result = project_state_readiness(self.root)

        self.assertFalse(result["ready"])
        self.assertTrue(
            any(item["reason"] == "human_markdown_link_internal" for item in result["blockers"])
        )

    def test_research_state_accepts_existing_relative_human_link(self) -> None:
        hypotheses = self.root / "hypotheses"
        hypotheses.mkdir()
        (hypotheses / "README.md").write_text("# 假设索引\n", encoding="utf-8")
        valid = VALID_RESEARCH_MD.replace(
            "暂无其他科研入口。",
            "- [假设索引](hypotheses/README.md)",
            1,
        )
        (self.root / "RESEARCH.md").write_text(valid, encoding="utf-8")

        result = project_state_readiness(self.root)

        self.assertTrue(result["ready"], result["blockers"])


if __name__ == "__main__":
    unittest.main()

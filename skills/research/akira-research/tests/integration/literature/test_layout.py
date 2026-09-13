from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from research_db_ops.completion.literature import literature_human_view_readiness  # noqa: E402
from research_db_ops.completion.human_literature import (  # noqa: E402
    LEGACY_NOTE_FORMAT_MARKER,
    NOTE_FORMAT_MARKER,
    migrate_versioned_human_literature_markers,
)
from research_db_ops.user_reading import confirmation_control, user_notes_block  # noqa: E402


def literature_readme(*paper_links: str, collection_links: tuple[str, ...] = ()) -> str:
    papers = "\n".join(f"- [{Path(link).stem}](<papers/{link}>)" for link in paper_links) or "不适用：当前没有论文。"
    collections = (
        "\n".join(f"- [{Path(link).stem}](<collections/{link}>)" for link in collection_links)
        or "不适用：当前没有集合。"
    )
    return (
        "# Literature\n\n"
        "## Navigation\n\n- [Research](../RESEARCH.md)\n\n"
        f"## Papers\n\n{papers}\n\n"
        f"## Collections\n\n{collections}\n"
    )


def collection(title: str, *paper_links: str) -> str:
    papers = "\n".join(f"- [{Path(link).stem}](<../papers/{link}>)" for link in paper_links) or "不适用：当前没有论文。"
    return (
        f"# Collection: {title}\n\n"
        "## Navigation\n\n- [Literature](../README.md)\n- [Research](../../RESEARCH.md)\n\n"
        "## Purpose\n\n围绕当前研究问题组织相关论文。\n\n"
        f"## Papers\n\n{papers}\n"
    )


def note(title: str = "论文") -> str:
    return (
        f"# {title}\n\n"
        + NOTE_FORMAT_MARKER
        + "\n\n| 项目 | 信息 |\n"
        + "| --- | --- |\n"
        + "| 中文译题 | — |\n"
        + "| 第一作者 | Wang |\n"
        + "| 期刊 / 会议 | Journal |\n"
        + "| 年份 | 2026 |\n"
        + "| DOI | 10.0000/example |\n"
        + "| PMID / PMCID | — |\n"
        + "| Paper ID | P000001 |\n"
        + "| 论文类型 | 原始研究 |\n"
        + "| 当前阅读用途 | 证据核验 |\n"
        + "| 本地全文 | [PDF](<Paper title - Wang - 2026.pdf>) |\n\n"
        + confirmation_control("top")
        + "\n\n## 三句话总结\n\n内容。\n\n"
        + "## 为什么值得读\n\n内容。\n\n"
        + "## 论文逻辑\n\n内容。\n\n"
        + "## 方法拆解\n\n内容。\n\n"
        + "## 实验逻辑\n\n### 实验 1：主实验\n\n内容。\n\n"
        + "## 数据直接显示什么\n\n内容。\n\n"
        + "## 作者如何解释\n\n内容。\n\n"
        + "## 我们的证据评估\n\n内容。\n\n"
        + "## 关键图表与定位\n\n内容。\n\n"
        + "## 可复用内容\n\n内容。\n\n"
        + "## 科研启发\n\n内容。\n\n"
        + "## 结论边界\n\n内容。\n\n"
        + "## 我的笔记\n\n"
        + user_notes_block()
        + "\n\n"
        + confirmation_control("bottom")
        + "\n"
    )


class LiteratureHumanViewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_missing_literature_directory_is_valid(self) -> None:
        result = literature_human_view_readiness(self.root)
        self.assertTrue(result["ready"])
        self.assertEqual(result["blockers"], [])

    def test_human_papers_directory_accepts_markdown_and_pdf(self) -> None:
        papers = self.root / "literature" / "papers"
        collections = self.root / "literature" / "collections"
        papers.mkdir(parents=True)
        collections.mkdir()
        (papers / "Paper title - Wang - 2026.md").write_text(note("Paper title"), encoding="utf-8")
        (papers / "Paper title - Wang - 2026.pdf").write_bytes(b"%PDF")
        (self.root / "RESEARCH.md").write_text("# Research\n", encoding="utf-8")
        (collections / "核心方法.md").write_text(
            collection("核心方法", "Paper title - Wang - 2026.md"), encoding="utf-8"
        )
        (self.root / "literature" / "README.md").write_text(
            literature_readme(
                "Paper title - Wang - 2026.md",
                collection_links=("核心方法.md",),
            ),
            encoding="utf-8",
        )

        result = literature_human_view_readiness(self.root)

        self.assertTrue(result["ready"], result["blockers"])
        self.assertEqual(result["blockers"], [])

    def test_legacy_note_without_type_marker_requires_migration_unless_grandfathered(self) -> None:
        papers = self.root / "literature" / "papers"
        papers.mkdir(parents=True)
        legacy = (
            "# Legacy paper\n\n"
            + confirmation_control("top")
            + "\n\n## 三句话总结\n\n旧格式内容。\n\n"
            + confirmation_control("bottom")
            + "\n"
        )
        (papers / "Legacy paper - Wang - 2024.md").write_text(legacy, encoding="utf-8")

        result = literature_human_view_readiness(self.root)

        self.assertFalse(result["ready"])
        self.assertTrue(
            any(item["reason"] == "human_literature_note_legacy_format" for item in result["blockers"])
        )

    def test_modern_note_requires_type_marker(self) -> None:
        papers = self.root / "literature" / "papers"
        papers.mkdir(parents=True)
        modern_without_marker = note().replace(NOTE_FORMAT_MARKER + "\n\n", "", 1)
        (papers / "Paper title - Wang - 2026.md").write_text(modern_without_marker, encoding="utf-8")

        result = literature_human_view_readiness(self.root)

        self.assertFalse(result["ready"])
        self.assertEqual(result["blockers"][0]["reason"], "human_literature_note_structure_invalid")
        self.assertIn("akira:literature-note", result["blockers"][0]["detail"])

    def test_versioned_marker_requires_migration(self) -> None:
        papers = self.root / "literature" / "papers"
        papers.mkdir(parents=True)
        old = note().replace(NOTE_FORMAT_MARKER, LEGACY_NOTE_FORMAT_MARKER, 1)
        (papers / "Paper title - Wang - 2026.md").write_text(old, encoding="utf-8")

        result = literature_human_view_readiness(self.root)

        self.assertFalse(result["ready"])
        self.assertTrue(
            any(item["reason"] == "human_literature_versioned_marker" for item in result["blockers"])
        )

    def test_note_requires_fixed_metadata_fields(self) -> None:
        papers = self.root / "literature" / "papers"
        papers.mkdir(parents=True)
        malformed = note().replace("| Paper ID | P000001 |\n", "", 1)
        (papers / "Paper title - Wang - 2026.md").write_text(malformed, encoding="utf-8")

        result = literature_human_view_readiness(self.root)

        self.assertFalse(result["ready"])
        self.assertEqual(result["blockers"][0]["reason"], "human_literature_note_structure_invalid")
        self.assertIn("Paper ID", result["blockers"][0]["detail"])

    def test_note_requires_fixed_h2_order_but_ignores_user_note_headings(self) -> None:
        papers = self.root / "literature" / "papers"
        papers.mkdir(parents=True)
        with_user_heading = note().replace(
            "<!-- akira:user-notes:start -->\n\n",
            "<!-- akira:user-notes:start -->\n\n## 用户自己的二级标题\n\n",
            1,
        )
        (self.root / "RESEARCH.md").write_text("# Research\n", encoding="utf-8")
        (papers / "Paper title - Wang - 2026.md").write_text(with_user_heading, encoding="utf-8")
        (papers / "Paper title - Wang - 2026.pdf").write_bytes(b"%PDF")
        (self.root / "literature" / "README.md").write_text(
            literature_readme("Paper title - Wang - 2026.md"), encoding="utf-8"
        )
        self.assertTrue(literature_human_view_readiness(self.root)["ready"])

        wrong_order = note().replace(
            "## 数据直接显示什么\n\n内容。\n\n## 作者如何解释",
            "## 作者如何解释\n\n内容。\n\n## 数据直接显示什么",
            1,
        )
        (papers / "Paper title - Wang - 2026.md").write_text(wrong_order, encoding="utf-8")
        result = literature_human_view_readiness(self.root)
        self.assertFalse(result["ready"])
        self.assertEqual(result["blockers"][0]["reason"], "human_literature_note_structure_invalid")
        self.assertIn("二级标题必须固定", result["blockers"][0]["detail"])

    def test_note_filename_must_match_author_and_year_metadata(self) -> None:
        papers = self.root / "literature" / "papers"
        papers.mkdir(parents=True)
        (papers / "Paper title - Li - 2025.md").write_text(note("Paper title"), encoding="utf-8")

        result = literature_human_view_readiness(self.root)

        self.assertFalse(result["ready"])
        self.assertTrue(
            any(item["reason"] == "human_literature_filename_invalid" for item in result["blockers"])
        )

    def test_literature_readme_must_cover_notes_and_collections(self) -> None:
        literature = self.root / "literature"
        papers = literature / "papers"
        collections = literature / "collections"
        papers.mkdir(parents=True)
        collections.mkdir()
        (self.root / "RESEARCH.md").write_text("# Research\n", encoding="utf-8")
        (papers / "Paper title - Wang - 2026.md").write_text(note("Paper title"), encoding="utf-8")
        (collections / "核心方法.md").write_text(
            collection("核心方法", "Paper title - Wang - 2026.md"), encoding="utf-8"
        )
        (literature / "README.md").write_text(
            literature_readme(collection_links=("核心方法.md",)), encoding="utf-8"
        )

        result = literature_human_view_readiness(self.root)

        self.assertFalse(result["ready"])
        self.assertTrue(
            any(item["reason"] == "human_literature_readme_missing_link" for item in result["blockers"])
        )

    def test_collection_uses_fixed_structure_and_only_links_human_papers(self) -> None:
        literature = self.root / "literature"
        papers = literature / "papers"
        collections = literature / "collections"
        papers.mkdir(parents=True)
        collections.mkdir()
        (self.root / "RESEARCH.md").write_text("# Research\n", encoding="utf-8")
        paper_name = "Paper title - Wang - 2026.md"
        (papers / paper_name).write_text(note("Paper title"), encoding="utf-8")
        (collections / "核心方法.md").write_text(
            "# 核心方法\n\n- [Paper](../papers/Paper title - Wang - 2026.md)\n",
            encoding="utf-8",
        )
        (literature / "README.md").write_text(
            literature_readme(paper_name, collection_links=("核心方法.md",)), encoding="utf-8"
        )

        result = literature_human_view_readiness(self.root)

        self.assertFalse(result["ready"])
        self.assertTrue(
            any(item["reason"] == "human_literature_collection_structure_invalid" for item in result["blockers"])
        )

    def test_marker_migration_rewrites_only_legacy_marker(self) -> None:
        papers = self.root / "literature" / "papers"
        papers.mkdir(parents=True)
        path = papers / "Paper title - Wang - 2026.md"
        old = note("Paper title").replace(NOTE_FORMAT_MARKER, LEGACY_NOTE_FORMAT_MARKER, 1)
        path.write_text(old, encoding="utf-8")

        result = migrate_versioned_human_literature_markers(self.root)

        migrated = path.read_text(encoding="utf-8")
        self.assertEqual(result["migrated_paths"], ["literature/papers/Paper title - Wang - 2026.md"])
        self.assertIn(NOTE_FORMAT_MARKER, migrated)
        self.assertNotIn(LEGACY_NOTE_FORMAT_MARKER, migrated)
        self.assertEqual(migrated.replace(NOTE_FORMAT_MARKER, LEGACY_NOTE_FORMAT_MARKER, 1), old)

    def test_machine_readable_artifact_in_human_area_is_rejected(self) -> None:
        papers = self.root / "literature" / "papers"
        papers.mkdir(parents=True)
        (papers / "paper.xml").write_text("<article/>", encoding="utf-8")

        result = literature_human_view_readiness(self.root)

        self.assertFalse(result["ready"])
        self.assertEqual(result["blockers"][0]["reason"], "human_literature_non_readable_file")
        self.assertEqual(result["blockers"][0]["path"], "literature/papers/paper.xml")

    def test_old_state_directories_are_rejected(self) -> None:
        ad_hoc = self.root / "literature" / "to-read"
        ad_hoc.mkdir(parents=True)
        (ad_hoc / "paper.md").write_text("# old state directory\n", encoding="utf-8")

        result = literature_human_view_readiness(self.root)

        self.assertFalse(result["ready"])
        self.assertEqual(result["blockers"][0]["reason"], "human_literature_unexpected_top_level")
        self.assertEqual(result["blockers"][0]["path"], "literature/to-read")

    def test_human_paper_note_requires_confirmation_controls(self) -> None:
        papers = self.root / "literature" / "papers"
        papers.mkdir(parents=True)
        (papers / "Paper title - Wang - 2026.md").write_text("# 缺确认框\n", encoding="utf-8")

        result = literature_human_view_readiness(self.root)

        self.assertFalse(result["ready"])
        self.assertEqual(
            result["blockers"][0]["reason"],
            "human_literature_confirmation_controls_missing",
        )

    def test_unregistered_nested_human_directory_is_rejected(self) -> None:
        nested = self.root / "literature" / "papers" / "topic"
        nested.mkdir(parents=True)
        (nested / "README.md").write_text("# note\n", encoding="utf-8")

        result = literature_human_view_readiness(self.root)

        self.assertFalse(result["ready"])
        self.assertEqual(
            result["blockers"][0]["reason"],
            "human_literature_unregistered_legacy_file",
        )

    def test_pdf_without_matching_markdown_note_is_rejected(self) -> None:
        papers = self.root / "literature" / "papers"
        papers.mkdir(parents=True)
        (papers / "Paper title - Wang - 2026.pdf").write_bytes(b"%PDF")

        result = literature_human_view_readiness(self.root)

        self.assertFalse(result["ready"])
        self.assertEqual(result["blockers"][0]["reason"], "human_literature_pdf_without_note")


if __name__ == "__main__":
    unittest.main()

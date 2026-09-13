from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from research_db_core import init_database  # noqa: E402
from research_db_ops.completion.project import research_tree_completion_readiness  # noqa: E402
from research_db_ops.project import (  # noqa: E402
    get_research_tree,
    record_research_edge,
    record_research_node,
    render_research_tree_view,
    set_research_tree_state,
)


class ResearchTreeViewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "RESEARCH.md").write_text("# Research\n", encoding="utf-8")
        init_database(self.root)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _record_large_tree(self) -> dict[str, int]:
        hypothesis_dir = self.root / "hypotheses"
        hypothesis_dir.mkdir()
        record_research_node(
            self.root,
            {
                "slug": "ecology-root",
                "kind": "objective",
                "label": "环境相关菌与宿主粪便生态对应关系",
                "workflow_status": "active",
                "branch_priority": "primary",
            },
        )
        for index, label in enumerate(
            (
                "环境相关菌在 yak feces 中更多？",
                "环境相关菌在 yak feces 中更分散？",
                "环境相关菌在更多 yak 个体中出现？",
                "yak feces 是否天生更保留环境丰度排序？",
            ),
            start=1,
        ):
            artifact = hypothesis_dir / f"alternative-{index}.md"
            artifact.write_text(f"# Hypothesis {index}\n", encoding="utf-8")
            record_research_node(
                self.root,
                {
                    "slug": f"alternative-{index}",
                    "kind": "hypothesis",
                    "label": label,
                    "parent_slug": "ecology-root",
                    "workflow_status": "closed",
                    "branch_priority": "secondary",
                    "artifact_path": artifact.relative_to(self.root).as_posix(),
                    "closure_reason": f"当前证据不支持替代解释 {index}。",
                },
            )
        record_research_node(
            self.root,
            {
                "slug": "matched-correspondence",
                "kind": "question",
                "label": "真实环境与当地 feces 是否存在 matched ecological correspondence？",
                "parent_slug": "ecology-root",
                "workflow_status": "active",
                "branch_priority": "primary",
            },
        )
        record_research_node(
            self.root,
            {
                "slug": "yak-advantage",
                "kind": "question",
                "label": "yak matched advantage 是否高于 cattle / sheep？",
                "parent_slug": "matched-correspondence",
                "workflow_status": "open",
                "branch_priority": "primary",
            },
        )
        for index in range(1, 9):
            record_research_node(
                self.root,
                {
                    "slug": f"mechanism-{index}",
                    "kind": "hypothesis",
                    "label": f"机制候选 {index}",
                    "parent_slug": "yak-advantage",
                    "workflow_status": "open",
                    "branch_priority": "secondary",
                },
            )
        set_research_tree_state(
            self.root,
            {"root_slug": "ecology-root", "active_slug": "matched-correspondence"},
        )
        tree = get_research_tree(self.root, limit=100)
        return {str(node["slug"]): int(node["id"]) for node in tree["nodes"]}

    def test_render_keeps_sibling_hypotheses_under_one_parent_in_one_large_graph(self) -> None:
        ids = self._record_large_tree()
        result = render_research_tree_view(self.root)
        path = self.root / result["path"]
        text = path.read_text(encoding="utf-8")

        self.assertEqual(text.count("```mermaid"), 1)
        self.assertIn("subgraph", text)
        root_id = ids["ecology-root"]
        sibling_ids = [ids[f"alternative-{index}"] for index in range(1, 5)]
        for child_id in sibling_ids:
            self.assertIn(f"N{root_id} --> N{child_id}", text)
        for left, right in zip(sibling_ids, sibling_ids[1:]):
            self.assertNotIn(f"N{left} --> N{right}", text)
            self.assertNotIn(f"N{right} --> N{left}", text)
        self.assertGreaterEqual(len(re.findall(r"(?m)^\s*N\d+[\[\{(]", text)), 15)
        self.assertIn("[打开](../hypotheses/alternative-1.md)", text)

    def test_completion_requires_generated_human_view(self) -> None:
        self._record_large_tree()

        readiness = research_tree_completion_readiness(self.root)

        self.assertFalse(readiness["ready"])
        self.assertTrue(
            any(item["reason"] == "research_tree_view_missing" for item in readiness["blockers"])
        )

    def test_completion_rejects_visual_edge_without_canonical_relation(self) -> None:
        ids = self._record_large_tree()
        path = self.root / render_research_tree_view(self.root)["path"]
        text = path.read_text(encoding="utf-8")
        extra = f"    N{ids['alternative-1']} --> N{ids['alternative-2']}\n"
        text = text.replace("```\n\n## Node Index", extra + "```\n\n## Node Index", 1)
        path.write_text(text, encoding="utf-8")

        readiness = research_tree_completion_readiness(self.root)

        self.assertFalse(readiness["ready"])
        self.assertTrue(
            any(item["reason"] == "research_tree_view_extra_edge" for item in readiness["blockers"])
        )

    def test_completion_rejects_multiple_mermaid_graphs(self) -> None:
        self._record_large_tree()
        path = self.root / render_research_tree_view(self.root)["path"]
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            "## Node Index",
            "```mermaid\nflowchart TD\n```\n\n## Node Index",
            1,
        )
        path.write_text(text, encoding="utf-8")

        readiness = research_tree_completion_readiness(self.root)

        self.assertFalse(readiness["ready"])
        self.assertTrue(
            any(
                item["reason"] == "research_tree_view_mermaid_block_invalid"
                for item in readiness["blockers"]
            )
        )

    def test_completion_allows_visual_grouping_change_without_edge_change(self) -> None:
        ids = self._record_large_tree()
        path = self.root / render_research_tree_view(self.root)["path"]
        text = path.read_text(encoding="utf-8")
        node_prefix = f"    N{ids['matched-correspondence']}"
        lines = text.splitlines()
        declaration_index = next(
            index for index, line in enumerate(lines) if line.startswith(node_prefix) and "-->" not in line
        )
        declaration = lines[declaration_index]
        lines[declaration_index : declaration_index + 1] = [
            '    subgraph VISUAL_ONLY["当前问题"]',
            "        direction LR",
            "    " + declaration,
            "    end",
        ]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        readiness = research_tree_completion_readiness(self.root)

        self.assertTrue(readiness["ready"], readiness["blockers"])

    def test_completion_rejects_missing_canonical_edge(self) -> None:
        ids = self._record_large_tree()
        path = self.root / render_research_tree_view(self.root)["path"]
        text = path.read_text(encoding="utf-8")
        required = f"    N{ids['ecology-root']} --> N{ids['alternative-1']}\n"
        self.assertIn(required, text)
        path.write_text(text.replace(required, "", 1), encoding="utf-8")

        readiness = research_tree_completion_readiness(self.root)

        self.assertFalse(readiness["ready"])
        self.assertTrue(
            any(item["reason"] == "research_tree_view_missing_edge" for item in readiness["blockers"])
        )

    def test_semantic_relation_is_rendered_and_validated_separately_from_parent_edge(self) -> None:
        ids = self._record_large_tree()
        record_research_edge(
            self.root,
            {
                "source_slug": "mechanism-1",
                "relation": "alternative_to",
                "target_slug": "mechanism-2",
                "note": "两个机制候选互为竞争解释。",
            },
        )
        path = self.root / render_research_tree_view(self.root)["path"]
        text = path.read_text(encoding="utf-8")

        self.assertIn(
            f"N{ids['mechanism-1']} -. alternative_to .-> N{ids['mechanism-2']}",
            text,
        )
        self.assertTrue(research_tree_completion_readiness(self.root)["ready"])


if __name__ == "__main__":
    unittest.main()

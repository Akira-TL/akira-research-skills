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
FIXTURE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIXTURE_DIR))

from blackbox_fixtures import ANALYSIS, DATASET, DESIGN, HYPOTHESIS, INTERPRETATION, RESEARCH_MD, STUDY  # noqa: E402

from research_db_core import database_path, init_database  # noqa: E402
from research_db_ops.communication import (  # noqa: E402
    record_communication,
    record_journal,
    record_target_workspace,
    tag_communication_release,
)
from research_db_ops.completion import validate_completion  # noqa: E402
from research_db_ops.completion.human import core_human_artifact_readiness  # noqa: E402
from research_db_ops.completion.project import research_tree_completion_readiness  # noqa: E402
from research_db_ops.project import (  # noqa: E402
    get_research_tree,
    record_research_node,
    render_research_tree_view,
    set_research_tree_state,
)
from research_db_support.storage import ResearchDbError  # noqa: E402




class ResearchReleaseBlackboxTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "RESEARCH.md").write_text(RESEARCH_MD, encoding="utf-8")
        init_database(self.root)
        subprocess.run(["git", "init", str(self.root)], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", str(self.root), "config", "user.email", "research@example.test"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.root), "config", "user.name", "Research Blackbox"],
            check=True,
        )
        self._write_human_chain()
        self._seed_core_objects()
        self._record_research_tree()
        render_research_tree_view(self.root)
        self.scientific_commit = self._commit("RESEARCH: establish canonical scientific chain")
        with closing(sqlite3.connect(database_path(self.root))) as connection, connection:
            connection.execute(
                "UPDATE hypothesis_sets SET status='frozen', freeze_commit=? WHERE slug='main'",
                (self.scientific_commit,),
            )
            connection.execute(
                "UPDATE research_designs SET status='frozen', freeze_commit=? WHERE slug='main'",
                (self.scientific_commit,),
            )
        self._commit("RESEARCH: freeze canonical research design")
        self._prepare_venue_neutral_manuscript()
        self._prepare_target("NC", "Nature Communications")

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

    def _write_human_chain(self) -> None:
        files = {
            "hypotheses/main.md": HYPOTHESIS,
            "designs/main.md": DESIGN,
            "study/main/README.md": STUDY,
            "data/main/README.md": DATASET,
            "analysis/main/README.md": ANALYSIS,
            "interpretation/main.md": INTERPRETATION,
            "hypotheses/README.md": (
                "# Hypotheses\n\n## Objects\n\n- [配对替代解释](main.md)\n\n"
                "## Relations\n\n- [配对替代解释](main.md) → [配对研究设计](../designs/main.md)\n"
            ),
            "designs/README.md": (
                "# Designs\n\n## Objects\n\n- [配对研究设计](main.md)\n\n"
                "## Relations\n\n- [配对研究设计](main.md) → [配对替代解释](../hypotheses/main.md), "
                "[配对研究实施](../study/main/README.md), [配对分析](../analysis/main/README.md)\n"
            ),
            "study/README.md": (
                "# Studies\n\n## Objects\n\n- [配对研究实施](main/README.md)\n\n"
                "## Relations\n\n- [配对研究实施](main/README.md) → [配对研究设计](../designs/main.md), "
                "[配对数据](../data/main/README.md)\n"
            ),
            "data/README.md": (
                "# Data\n\n## Objects\n\n- [配对数据](main/README.md)\n\n"
                "## Relations\n\n- [配对数据](main/README.md) → [配对研究实施](../study/main/README.md), "
                "[配对分析](../analysis/main/README.md)\n"
            ),
            "analysis/README.md": (
                "# Analyses\n\n## Objects\n\n- [配对分析](main/README.md)\n\n"
                "## Relations\n\n- [配对分析](main/README.md) → [配对研究设计](../designs/main.md), "
                "[配对数据](../data/main/README.md)\n"
            ),
            "interpretation/README.md": (
                "# Interpretations\n\n## Objects\n\n- [配对结果解释](main.md)\n\n"
                "## Relations\n\n- [配对结果解释](main.md) → [配对分析](../analysis/main/README.md)\n"
            ),
            "scripts/analyses/main.py": "print('reproduce matched analysis')\n",
        }
        for relative, text in files.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    def _seed_core_objects(self) -> None:
        now = "2026-09-13T00:00:00+00:00"
        with closing(sqlite3.connect(database_path(self.root))) as connection, connection:
            connection.execute(
                """
                INSERT INTO hypothesis_sets(
                    slug, title, target_uncertainty, artifact_path, status, created_at, updated_at
                ) VALUES ('main', 'Matched correspondence alternatives',
                          '牦牛与当地环境的对应关系是否强于其他反刍动物？',
                          'hypotheses/main.md', 'draft', ?, ?)
                """,
                (now, now),
            )
            hypothesis_id = int(
                connection.execute("SELECT id FROM hypothesis_sets WHERE slug='main'").fetchone()[0]
            )
            connection.execute(
                """
                INSERT INTO research_designs(
                    slug, title, hypothesis_set_id, target_estimand, primary_outcome,
                    experimental_unit, artifact_path, status, feasibility_status,
                    created_at, updated_at
                ) VALUES ('main', 'Matched comparison', ?,
                          '牦牛 匹配生态对应关系 减对照反刍动物 匹配生态对应关系',
                          '匹配生态对应关系', '地理配对单元', 'designs/main.md',
                          'draft', 'ready', ?, ?)
                """,
                (hypothesis_id, now, now),
            )
            design_id = int(
                connection.execute("SELECT id FROM research_designs WHERE slug='main'").fetchone()[0]
            )
            connection.execute(
                """
                INSERT INTO studies(
                    slug, title, design_id, study_type, status, provenance_path,
                    started_at, created_at, updated_at
                ) VALUES ('main', 'Matched field execution', ?, 'observational', 'in_progress',
                          'study/main/README.md', ?, ?, ?)
                """,
                (design_id, now, now, now),
            )
            study_id = int(connection.execute("SELECT id FROM studies WHERE slug='main'").fetchone()[0])
            connection.execute(
                """
                INSERT INTO datasets(
                    slug, title, source, received_at, unit_of_inference, provenance_path,
                    status, created_at, updated_at, study_id
                ) VALUES ('main', 'Matched ecology dataset', 'matched field study', ?,
                          '地理配对单元', 'data/main/README.md', 'active', ?, ?, ?)
                """,
                (now, now, now, study_id),
            )
            dataset_id = int(connection.execute("SELECT id FROM datasets WHERE slug='main'").fetchone()[0])
            connection.execute(
                """
                INSERT INTO analysis_runs(
                    slug, title, analysis_mode, status, target_uncertainty, estimand,
                    unit_of_inference, primary_analysis, analysis_path, code_path,
                    started_at, created_at, updated_at, design_id
                ) VALUES ('main', 'Matched advantage analysis', 'exploratory', 'planned',
                          '牦牛 匹配生态对应关系 是否强于对照反刍动物？',
                          '牦牛 匹配生态对应关系 减对照反刍动物 匹配生态对应关系',
                          '地理配对单元', '估计预定义物种间 contrast',
                          'analysis/main/README.md', 'scripts/analyses/main.py', ?, ?, ?, ?)
                """,
                (now, now, now, design_id),
            )
            analysis_id = int(
                connection.execute("SELECT id FROM analysis_runs WHERE slug='main'").fetchone()[0]
            )
            connection.execute(
                "INSERT INTO analysis_inputs(analysis_id, dataset_id, role) VALUES (?, ?, 'primary')",
                (analysis_id, dataset_id),
            )

    def _record_research_tree(self) -> None:
        record_research_node(
            self.root,
            {
                "slug": "ecology-root",
                "kind": "objective",
                "label": "环境与宿主粪便的生态对应关系",
                "workflow_status": "active",
                "branch_priority": "primary",
            },
        )
        alternatives = (
            "环境相关菌在牦牛粪便中更多？",
            "环境相关菌在牦牛粪便中更分散？",
            "环境相关菌在更多牦牛个体中出现？",
            "牦牛粪便是否天然保留环境丰度排序？",
        )
        for index, label in enumerate(alternatives, start=1):
            record_research_node(
                self.root,
                {
                    "slug": f"alternative-{index}",
                    "kind": "hypothesis",
                    "label": label,
                    "parent_slug": "ecology-root",
                    "workflow_status": "closed",
                    "branch_priority": "secondary",
                    "closure_reason": f"当前证据否定或限定基础替代解释 {index}。",
                },
            )
        record_research_node(
            self.root,
            {
                "slug": "matched-question",
                "kind": "question",
                "label": "当地环境与当地粪便是否存在 matched ecological correspondence？",
                "parent_slug": "ecology-root",
                "workflow_status": "active",
                "branch_priority": "primary",
            },
        )
        record_research_node(
            self.root,
            {
                "slug": "formal-hypothesis",
                "kind": "hypothesis",
                "label": "牦牛的地理配对生态对应关系是否强于对照反刍动物？",
                "parent_slug": "matched-question",
                "workflow_status": "open",
                "branch_priority": "primary",
                "artifact_path": "hypotheses/main.md",
            },
        )
        record_research_node(
            self.root,
            {
                "slug": "matched-design",
                "kind": "design",
                "label": "Matched comparison design",
                "parent_slug": "formal-hypothesis",
                "workflow_status": "open",
                "branch_priority": "primary",
                "artifact_path": "designs/main.md",
            },
        )
        record_research_node(
            self.root,
            {
                "slug": "matched-study",
                "kind": "study",
                "label": "Matched field execution",
                "parent_slug": "matched-design",
                "workflow_status": "open",
                "branch_priority": "primary",
                "artifact_path": "study/main/README.md",
            },
        )
        record_research_node(
            self.root,
            {
                "slug": "matched-analysis",
                "kind": "analysis",
                "label": "Matched advantage analysis",
                "parent_slug": "matched-study",
                "workflow_status": "active",
                "branch_priority": "primary",
                "artifact_path": "analysis/main/README.md",
            },
        )
        record_research_node(
            self.root,
            {
                "slug": "matched-interpretation",
                "kind": "claim",
                "label": "Matched ecology interpretation",
                "parent_slug": "matched-analysis",
                "workflow_status": "open",
                "branch_priority": "primary",
                "artifact_path": "interpretation/main.md",
            },
        )
        set_research_tree_state(
            self.root,
            {"root_slug": "ecology-root", "active_slug": "matched-analysis"},
        )

    def _prepare_venue_neutral_manuscript(self) -> None:
        manuscript = self.root / "communication" / "yak-ecology" / "manuscript.md"
        manuscript.parent.mkdir(parents=True, exist_ok=True)
        manuscript.write_text(
            "# 当地环境与牦牛粪便的生态对应关系\n\n"
            "本稿件保持目标期刊中立，只陈述当前 canonical scientific state。\n",
            encoding="utf-8",
        )
        record_communication(
            self.root,
            {
                "slug": "yak-ecology",
                "title": "当地环境与牦牛粪便的生态对应关系",
                "purpose": "形成目标期刊中立的原始研究论文稿件",
                "audience": "科研读者",
                "source_commit": self.scientific_commit,
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
        self.manuscript_commit = self._commit("DOCS: add venue-neutral manuscript")

    def _write_build_script(self, workspace: Path) -> None:
        (workspace / "build.py").write_text(
            """from __future__ import annotations

import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output-dir", required=True)
args = parser.parse_args()
out = Path(args.output_dir)
out.mkdir(parents=True, exist_ok=True)
(out / "manuscript.docx").write_bytes(b"docx blackbox output")
(out / "manuscript.pdf").write_bytes(b"pdf blackbox output")
""",
            encoding="utf-8",
        )

    def _write_target_manifest(self, workspace: Path, code: str, source_commit: str) -> None:
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

    def _prepare_target(self, code: str, name: str) -> None:
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
        self._write_build_script(workspace)
        (workspace / "journal.json").write_text(
            json.dumps({"journal_code": code}, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        (workspace / "QA.md").write_text(
            "# QA\n\n固定黑盒已核对目标 build source 与页面验收职责。\n",
            encoding="utf-8",
        )
        self._write_target_manifest(workspace, code, self.manuscript_commit)
        record_target_workspace(
            self.root,
            {
                "slug": "yak-ecology",
                "journal_code": code,
                "source_commit": self.manuscript_commit,
            },
        )
        self._commit(f"BUILD: prepare {code} target release source")

    def _checkpoint(self, version: str) -> dict[str, object]:
        result = tag_communication_release(
            self.root,
            {"slug": "yak-ecology", "journal_code": "NC", "version": version},
        )
        self._commit(f"RESEARCH: record NC {version} checkpoint 追溯记录")
        return result

    def _refresh_target_after_manuscript_change(self) -> None:
        manuscript = self.root / "communication" / "yak-ecology" / "manuscript.md"
        manuscript.write_text(
            manuscript.read_text(encoding="utf-8")
            + "\n修订稿补充了结果边界说明，但仍保持同一 canonical source。\n",
            encoding="utf-8",
        )
        source_commit = self._commit("DOCS: revise canonical manuscript")
        workspace = self.root / "communication" / "yak-ecology" / "NC-release"
        self._write_target_manifest(workspace, "NC", source_commit)
        record_target_workspace(
            self.root,
            {"slug": "yak-ecology", "journal_code": "NC", "source_commit": source_commit},
        )
        self._commit("BUILD: refresh NC target after manuscript revision")

    def test_full_human_reading_and_release_chain(self) -> None:
        human = core_human_artifact_readiness(self.root)
        self.assertTrue(human["ready"], human["blockers"])

        tree_ready = research_tree_completion_readiness(self.root)
        self.assertTrue(tree_ready["ready"], tree_ready["blockers"])
        tree = get_research_tree(self.root, limit=None)
        ids = {str(row["slug"]): int(row["id"]) for row in tree["nodes"]}
        tree_text = (self.root / "research-tree" / "README.md").read_text(encoding="utf-8")
        for index in range(1, 5):
            self.assertIn(f"N{ids['ecology-root']} --> N{ids[f'alternative-{index}']}", tree_text)
        for left, right in zip(range(1, 4), range(2, 5)):
            self.assertNotIn(
                f"N{ids[f'alternative-{left}']} --> N{ids[f'alternative-{right}']}",
                tree_text,
            )

        research_home = (self.root / "RESEARCH.md").read_text(encoding="utf-8")
        for target in (
            "research-tree/README.md",
            "hypotheses/README.md",
            "designs/README.md",
            "study/README.md",
            "data/README.md",
            "analysis/README.md",
            "interpretation/README.md",
            "communication/yak-ecology/manuscript.md",
        ):
            self.assertIn(target, research_home)
            self.assertTrue((self.root / target).is_file())

        checkpoint_10 = self._checkpoint("1.0")
        self._refresh_target_after_manuscript_change()
        checkpoint_11 = self._checkpoint("1.1")
        self.assertNotEqual(checkpoint_10["commit"], checkpoint_11["commit"])

        with self.assertRaisesRegex(ResearchDbError, "连续"):
            tag_communication_release(
                self.root,
                {"slug": "yak-ecology", "journal_code": "NC", "version": "1.3"},
            )
        with self.assertRaisesRegex(ResearchDbError, "版本号.修订号"):
            tag_communication_release(
                self.root,
                {"slug": "yak-ecology", "journal_code": "NC", "version": "v1.2"},
            )

        release = tag_communication_release(
            self.root,
            {
                "slug": "yak-ecology",
                "journal_code": "NC",
                "version": "1.1",
                "release_date": "2026-09-13",
                "release_evidence_source": "user_confirmation",
                "release_evidence": "黑盒 fixture 明确模拟用户已确认该版本于该日真实公开。",
            },
        )
        self.assertEqual(release["commit"], checkpoint_11["commit"])
        self.assertEqual(release["tag"], "yak-ecology/NC-1.1-release-20260913")
        self._commit("RESEARCH: record public release 追溯记录")

        subprocess.run(
            ["git", "-C", str(self.root), "tag", "yak-ecology/NC-final"],
            check=True,
        )
        invalid = validate_completion(self.root)
        invalid_reasons = {item["reason"] for item in invalid["communication"]["blockers"]}
        self.assertIn("communication_release_tag_name_invalid", invalid_reasons)
        subprocess.run(
            ["git", "-C", str(self.root), "tag", "-d", "yak-ecology/NC-final"],
            check=True,
            capture_output=True,
        )

        workspace = self.root / "communication" / "yak-ecology" / "NC-release"
        (workspace / "manuscript.pdf").write_bytes(b"stored generated output")
        drifted = validate_completion(self.root)
        drift_reasons = {item["reason"] for item in drifted["communication"]["blockers"]}
        self.assertIn("communication_target_generated_output_stored", drift_reasons)
        (workspace / "manuscript.pdf").unlink()

        final = validate_completion(self.root)
        self.assertTrue(final["completion"], final["errors"])
        self.assertTrue(final["human_artifacts"]["ready"], final["human_artifacts"]["blockers"])
        self.assertTrue(final["research_tree"]["ready"], final["research_tree"]["blockers"])
        self.assertTrue(final["communication"]["ready"], final["communication"]["blockers"])
        self.assertFalse(any("/v1" in path or "_v1" in path for path in self._tracked_paths()))

    def _tracked_paths(self) -> list[str]:
        result = subprocess.run(
            ["git", "-C", str(self.root), "ls-files"],
            check=True,
            text=True,
            capture_output=True,
        )
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]


if __name__ == "__main__":
    unittest.main()

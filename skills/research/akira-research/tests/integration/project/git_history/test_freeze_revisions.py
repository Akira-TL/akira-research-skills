from __future__ import annotations

import sys
import unittest
from pathlib import Path

FIXTURE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIXTURE_DIR))

from git_fixtures import GitResearchProject, blockers_with_reason  # noqa: E402

from research_db_core import ResearchDbError  # noqa: E402
from research_db_ops.completion import validate_completion  # noqa: E402
from research_db_ops.completion.human.legacy import path_is_unchanged_since_baseline  # noqa: E402
from research_db_ops.downstream import record_analysis  # noqa: E402
from research_db_ops.project import list_freeze_revisions, record_freeze_revisions  # noqa: E402

CHANGED = "analysis_frozen_artifact_changed_after_freeze"


class FreezeRevisionTests(unittest.TestCase):
    subdirectory = ""

    def setUp(self) -> None:
        self.project = GitResearchProject(subdirectory=self.subdirectory)
        self.root = self.project.root

    def tearDown(self) -> None:
        self.project.cleanup()

    def _frozen_then_revised(self) -> str:
        freeze_commit = self.project.freeze_planned_analysis()
        self.project.record_result(freeze_commit)
        self.project.write("data/sleep/README.md", "# 数据来源\n\n受试者是独立推断单位。路径已更新。\n")
        return self.project.commit("DATA: update frozen provenance note")

    def test_unrecorded_change_blocks_with_commits_and_recorded_change_passes(self) -> None:
        revision_commit = self._frozen_then_revised()
        result = validate_completion(self.root)
        changed = blockers_with_reason(result, "downstream", CHANGED)
        self.assertEqual(len(changed), 1)
        self.assertEqual(
            changed[0]["changes"], [{"path": "data/sleep/README.md", "commits": [revision_commit]}]
        )
        pending = list_freeze_revisions(self.root, pending=True)["pending"]
        self.assertEqual([item["path"] for item in pending], ["data/sleep/README.md"])

        recorded = record_freeze_revisions(
            self.root,
            {
                "category": "path_migration",
                "reason": "更新冻结说明中的数据位置，不改变数据或分析计划。",
                "revisions": [{"path": "data/sleep/README.md", "revision_commit": revision_commit[:10]}],
            },
        )
        self.assertEqual(recorded["recorded"][0]["revision_commit"], revision_commit)
        self.project.commit("PROVENANCE: record freeze revision")

        result = validate_completion(self.root)
        self.assertEqual(blockers_with_reason(result, "downstream", CHANGED), [])
        self.assertEqual(
            [item["path"] for item in result["git"]["applied_freeze_revisions"]], ["data/sleep/README.md"]
        )
        self.assertEqual(list_freeze_revisions(self.root, pending=True)["pending"], [])

    def test_revision_must_name_a_commit_that_changed_the_object(self) -> None:
        self._frozen_then_revised()
        with self.assertRaisesRegex(ResearchDbError, "没有改变该对象内容"):
            record_freeze_revisions(
                self.root,
                {
                    "revision_commit": "HEAD",
                    "category": "substantive",
                    "reason": "错误的提交。",
                    "revisions": ["analysis/trajectory/README.md"],
                },
            )
        with self.assertRaises(ResearchDbError):
            record_freeze_revisions(
                self.root,
                {
                    "revision_commit": "HEAD",
                    "category": "cosmetic",
                    "reason": "x",
                    "revisions": ["data/sleep/README.md"],
                },
            )

    def test_unrecorded_later_change_still_blocks_after_earlier_revision(self) -> None:
        first = self._frozen_then_revised()
        record_freeze_revisions(
            self.root,
            {
                "revision_commit": first,
                "category": "redundant_checksum_removal",
                "reason": "删除重复的文件校验值。",
                "revisions": ["data/sleep/README.md"],
            },
        )
        self.project.write("data/sleep/README.md", "# 数据来源\n\n改成了不同的推断单位。\n")
        second = self.project.commit("DATA: substantive edit")
        changed = blockers_with_reason(validate_completion(self.root), "downstream", CHANGED)
        self.assertEqual(changed[0]["changes"][0]["commits"], [second])

    def test_legacy_grandfathering_survives_recorded_revisions_only(self) -> None:
        legacy = self.project.write("designs/legacy.md", "# 旧设计\n\nsha256: abc\n")
        baseline = self.project.commit("DESIGN: legacy baseline")
        self.assertTrue(path_is_unchanged_since_baseline(self.root, legacy, baseline))
        legacy.write_text("# 旧设计\n", encoding="utf-8")
        revision = self.project.commit("DESIGN: drop redundant checksum")
        self.assertFalse(path_is_unchanged_since_baseline(self.root, legacy, baseline))
        record_freeze_revisions(
            self.root,
            {
                "revision_commit": revision,
                "category": "redundant_checksum_removal",
                "reason": "冻结对象改由提交号 + 路径识别。",
                "revisions": ["designs/legacy.md"],
            },
        )
        self.assertTrue(path_is_unchanged_since_baseline(self.root, legacy, baseline))
        legacy.write_text("# 旧设计\n\n未提交修改。\n", encoding="utf-8")
        self.assertFalse(path_is_unchanged_since_baseline(self.root, legacy, baseline))

    def test_result_first_committed_outside_freeze_descendants_is_rejected(self) -> None:
        self.project.write("notes.md", "start\n")
        before = self.project.commit("START")
        self.project.git("branch", "early-result", before)
        freeze_commit = self.project.freeze_planned_analysis()
        self.project.git("checkout", "-q", "early-result")
        self.project.write("analysis/trajectory/outputs/primary.csv", "term,estimate\nslope,11.4\n")
        self.project.commit("RESULT: computed before freeze")
        self.project.git("checkout", "-q", "-")
        self.project.git("merge", "-q", "--no-ff", "-m", "MERGE: early result", "early-result")
        record_analysis(
            self.root,
            self.project.analysis_bundle(
                status="completed",
                freeze_commit=freeze_commit,
                artifacts=[{"role": "estimate", "path": "analysis/trajectory/outputs/primary.csv"}],
                observations=[
                    {"statement": "A result exists.", "source_path": "analysis/trajectory/outputs/primary.csv"}
                ],
            ),
        )
        self.project.commit("ANALYSIS: record result")
        result = validate_completion(self.root)
        late = blockers_with_reason(result, "downstream", "analysis_result_commit_not_after_freeze")
        self.assertEqual(late[0]["paths"], ["analysis/trajectory/outputs/primary.csv"])


class SubdirectoryFreezeRevisionTests(FreezeRevisionTests):
    subdirectory = "research"


if __name__ == "__main__":
    unittest.main()

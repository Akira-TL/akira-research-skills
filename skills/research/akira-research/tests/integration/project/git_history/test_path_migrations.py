from __future__ import annotations

import shutil
import sys
import unittest
from pathlib import Path

FIXTURE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIXTURE_DIR))

from git_fixtures import GitResearchProject, blockers_with_reason  # noqa: E402

from research_db_core import GITIGNORE_BEGIN, ResearchDbError  # noqa: E402
from research_db_ops.completion import validate_completion  # noqa: E402
from research_db_ops.completion.git import FreezeHistory  # noqa: E402
from research_db_ops.downstream import list_analyses  # noqa: E402
from research_db_ops.project import list_path_migrations, record_freeze_revisions, record_path_migration  # noqa: E402

MISSING = "analysis_plan_or_input_missing_at_freeze"
CHANGED = "analysis_frozen_artifact_changed_after_freeze"
RESEARCH_ENTRIES = ("RESEARCH.md", ".research", "data", "analysis")


class PathMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = GitResearchProject()
        self.top = self.project.top
        self.freeze_commit = self.project.freeze_planned_analysis()
        self.project.record_result(self.freeze_commit)
        self.original_note = (self.top / "data/sleep/README.md").read_text(encoding="utf-8")

    def tearDown(self) -> None:
        self.project.cleanup()

    def _move_into_research(self, *, edit_plan: bool = False) -> tuple[Path, str]:
        research = self.top / "research"
        research.mkdir()
        for name in RESEARCH_ENTRIES:
            shutil.move(str(self.top / name), str(research / name))
        if edit_plan:
            (research / "analysis/trajectory/README.md").write_text(
                "# 分析计划\n\n主要估计量为每日变化斜率。代码见 ../scripts。\n", encoding="utf-8"
            )
        return research, self.project.commit("MAINTENANCE: move research root into research/")

    def _record_root_move(self, research: Path, commit: str, **extra) -> dict:
        return record_path_migration(
            research,
            {
                "migration_commit": commit,
                "moves": [{"old_prefix": "", "new_prefix": "research/"}],
                "reason": "科研内容整体移入 research/ 子目录。",
                **extra,
            },
        )

    def test_root_move_rewrites_paths_and_old_freezes_still_verify(self) -> None:
        research, migration_commit = self._move_into_research()
        broken = validate_completion(research)
        self.assertTrue(blockers_with_reason(broken, "downstream", MISSING))

        preview = self._record_root_move(research, migration_commit, dry_run=True)
        self.assertEqual(preview["old_project_prefix"], "")
        rewrites = {(item["table"], item["column"]): item["new"] for item in preview["rewrites"]}
        self.assertEqual(rewrites[("analysis_runs", "code_path")], "../scripts/analyses/trajectory.py")
        self.assertNotIn(("analysis_runs", "analysis_path"), rewrites)
        self.assertEqual(list_path_migrations(research)["path_migrations"], [])

        result = self._record_root_move(research, migration_commit)
        self.assertTrue(result["gitignore_updated"])
        self.assertIn(GITIGNORE_BEGIN, (research / ".gitignore").read_text(encoding="utf-8"))
        analysis = list_analyses(research)["analyses"][0]
        self.assertEqual(analysis["code_path"], "../scripts/analyses/trajectory.py")
        self.project.commit("PROVENANCE: record directory migration")

        result = validate_completion(research)
        self.assertEqual(blockers_with_reason(result, "downstream", MISSING), [])
        self.assertEqual(blockers_with_reason(result, "downstream", CHANGED), [])
        self.assertTrue(any("应删除" in warning for warning in result["warnings"]))

        history = FreezeHistory(research)
        self.assertEqual(history.path_at(self.freeze_commit, "data/sleep/README.md"), "data/sleep/README.md")
        self.assertEqual(
            history.read(self.freeze_commit, "data/sleep/README.md").decode("utf-8"), self.original_note
        )

        with self.assertRaisesRegex(ResearchDbError, "已登记"):
            self._record_root_move(research, migration_commit)

    def test_content_edit_inside_migration_commit_needs_revision_note(self) -> None:
        research, migration_commit = self._move_into_research(edit_plan=True)
        self._record_root_move(research, migration_commit)
        self.project.commit("PROVENANCE: record directory migration")
        changed = blockers_with_reason(validate_completion(research), "downstream", CHANGED)
        self.assertEqual(
            changed[0]["changes"], [{"path": "analysis/trajectory/README.md", "commits": [migration_commit]}]
        )
        record_freeze_revisions(
            research,
            {
                "revision_commit": migration_commit,
                "category": "path_migration",
                "reason": "迁移时更新代码位置说明。",
                "revisions": ["analysis/trajectory/README.md"],
            },
        )
        self.assertEqual(blockers_with_reason(validate_completion(research), "downstream", CHANGED), [])

    def test_chained_migrations_map_back_to_the_freeze_commit(self) -> None:
        research, migration_commit = self._move_into_research()
        self._record_root_move(research, migration_commit)
        self.project.commit("PROVENANCE: record directory migration")
        shutil.move(str(research / "data"), str(research / "datasets"))
        second = self.project.commit("MAINTENANCE: rename data directory")
        result = record_path_migration(
            research,
            {
                "migration_commit": second,
                "moves": [{"old_prefix": "research/data", "new_prefix": "research/datasets/"}],
                "reason": "数据目录改名。",
            },
        )
        rewritten = {item["old"]: item["new"] for item in result["rewrites"]}
        self.assertEqual(rewritten["data/sleep/README.md"], "datasets/sleep/README.md")
        self.project.commit("PROVENANCE: record data directory rename")
        history = FreezeHistory(research)
        self.assertEqual(history.path_at(self.freeze_commit, "datasets/sleep/raw.csv"), "data/sleep/raw.csv")
        result = validate_completion(research)
        self.assertEqual(blockers_with_reason(result, "downstream", MISSING), [])
        self.assertEqual(blockers_with_reason(result, "downstream", CHANGED), [])


if __name__ == "__main__":
    unittest.main()

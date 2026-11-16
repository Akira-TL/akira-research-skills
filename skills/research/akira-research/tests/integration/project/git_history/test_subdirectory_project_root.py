from __future__ import annotations

import sys
import unittest
from pathlib import Path

FIXTURE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIXTURE_DIR))

from git_fixtures import GitResearchProject, blockers_with_reason  # noqa: E402

from research_db_core import GITIGNORE_BEGIN, ResearchDbError  # noqa: E402
from research_db_ops import common  # noqa: E402
from research_db_ops.completion import validate_completion  # noqa: E402
from research_db_ops.project.research_git import _material_tip  # noqa: E402
from research_db_ops.completion.git import FreezeHistory  # noqa: E402
from research_db_support.git_layout import commit_has_path, git_layout  # noqa: E402


class SubdirectoryProjectRootTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = GitResearchProject(subdirectory="research")
        self.root = self.project.root

    def tearDown(self) -> None:
        self.project.cleanup()

    def test_layout_maps_project_paths_to_repository_paths(self) -> None:
        layout = git_layout(self.root)
        self.assertEqual(layout.prefix, "research/")
        self.assertEqual(layout.repo_path("data/x.csv"), "research/data/x.csv")
        self.assertEqual(layout.repo_path("../scripts/x.py"), "scripts/x.py")
        self.assertIsNone(layout.repo_path("../../outside.txt"))
        self.assertEqual(layout.project_path("scripts/x.py"), "../scripts/x.py")

    def test_local_paths_may_point_outside_research_root_but_inside_repository(self) -> None:
        self.project.write("../scripts/tool.py", "print(1)\n")
        self.assertEqual(
            common.local_path(self.root, "../scripts/tool.py", field="code_path"),
            "../scripts/tool.py",
        )
        outside = self.project.top.parent / f"{self.project.top.name}-outside.txt"
        outside.write_text("x\n", encoding="utf-8")
        try:
            with self.assertRaises(ResearchDbError):
                common.local_path(self.root, str(outside), field="code_path")
        finally:
            outside.unlink()

    def test_commit_lookups_use_repository_relative_object_names(self) -> None:
        self.project.write("data/a.txt", "a\n")
        self.project.write("../scripts/b.py", "b\n")
        commit = self.project.commit("DATA: add files")
        self.assertTrue(commit_has_path(self.root, commit, "data/a.txt"))
        self.assertTrue(commit_has_path(self.root, commit, "../scripts/b.py"))
        self.assertTrue(commit_has_path(self.root, commit, ".research/research.sqlite"))
        self.assertEqual(FreezeHistory(self.root).read(commit, "../scripts/b.py"), b"b\n")

    def test_branch_tip_ignores_database_only_commits_but_not_outside_code(self) -> None:
        self.project.write("data/a.txt", "a\n")
        start = self.project.commit("DATA: start")
        (self.root / ".research" / "research.sqlite").write_bytes(
            (self.root / ".research" / "research.sqlite").read_bytes() + b"\0"
        )
        database_only = self.project.commit("PROVENANCE: database only")
        self.assertEqual(_material_tip(self.root, start, database_only), start)
        self.project.write("../scripts/c.py", "c\n")
        code_change = self.project.commit("CODE: outside research root")
        self.assertEqual(_material_tip(self.root, start, code_change), code_change)

    def test_completion_accepts_subdirectory_root_and_tracks_outside_code(self) -> None:
        freeze_commit = self.project.freeze_planned_analysis()
        self.project.record_result(freeze_commit)

        result = validate_completion(self.root)
        self.assertEqual(result["git"]["project_prefix"], "research/")
        self.assertFalse(any("top-level" in error for error in result["errors"]), result["errors"])
        self.assertEqual(
            blockers_with_reason(result, "downstream", "analysis_plan_or_input_missing_at_freeze"), []
        )
        self.assertEqual(
            blockers_with_reason(result, "downstream", "analysis_frozen_artifact_changed_after_freeze"), []
        )

        self.project.write(self.project.code_path, "print('changed')\n")
        self.project.commit("CODE: change frozen analysis code")
        result = validate_completion(self.root)
        changed = blockers_with_reason(result, "downstream", "analysis_frozen_artifact_changed_after_freeze")
        self.assertEqual(len(changed), 1)
        self.assertEqual(changed[0]["paths"], ["../scripts/analyses/trajectory.py"])

    def test_managed_gitignore_lives_in_research_root(self) -> None:
        self.assertIn(GITIGNORE_BEGIN, (self.root / ".gitignore").read_text(encoding="utf-8"))
        result = validate_completion(self.root)
        self.assertFalse(any(".gitignore" in warning for warning in result["warnings"]))

        (self.root / ".gitignore").unlink()
        (self.project.top / ".gitignore").write_text(f"{GITIGNORE_BEGIN}\n.research/artifacts/\n", encoding="utf-8")
        result = validate_completion(self.root)
        self.assertTrue(any("research/.gitignore" in warning for warning in result["warnings"]))


if __name__ == "__main__":
    unittest.main()

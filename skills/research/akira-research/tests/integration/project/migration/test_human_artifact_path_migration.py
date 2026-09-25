from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[4] / "scripts"
RESEARCH_DB = SCRIPT_DIR / "research_db.py"
sys.path.insert(0, str(SCRIPT_DIR))

from research_db_core import database_path, init_database  # noqa: E402


class HumanArtifactPathMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "RESEARCH.md").write_text("# Research\n", encoding="utf-8")
        init_database(self.root)
        now = "2026-09-25T00:00:00+00:00"
        with sqlite3.connect(database_path(self.root)) as connection:
            connection.execute(
                """
                INSERT INTO datasets(
                    slug, title, identity, source, version, received_at,
                    unit_of_inference, provenance_path, status, created_at, updated_at
                ) VALUES (
                    'sample', 'Sample dataset', 'sha256:sample', 'fixture', 'v1', ?,
                    'paper', 'data/legacy-sample.md', 'active', ?, ?
                )
                """,
                (now, now, now),
            )
            connection.execute(
                """
                INSERT INTO analysis_runs(
                    slug, title, analysis_mode, status, target_uncertainty, estimand,
                    unit_of_inference, primary_analysis, analysis_path, code_path,
                    freeze_commit, started_at, completed_at, created_at, updated_at
                ) VALUES (
                    'model', 'Completed model', 'exploratory', 'completed',
                    'Does the result persist?', 'Descriptive audit result', 'paper',
                    'Fixed audit procedure', 'analysis/legacy-model.md',
                    'scripts/analyses/model.py', NULL, ?, ?, ?, ?
                )
                """,
                (now, now, now, now),
            )
            connection.commit()

        (self.root / "data" / "sample").mkdir(parents=True)
        (self.root / "analysis" / "model").mkdir(parents=True)
        (self.root / "data" / "legacy-sample.md").write_text("legacy dataset\n", encoding="utf-8")
        (self.root / "analysis" / "legacy-model.md").write_text("legacy analysis\n", encoding="utf-8")
        (self.root / "data" / "sample" / "README.md").write_text("# Dataset: Sample dataset\n", encoding="utf-8")
        (self.root / "analysis" / "model" / "README.md").write_text("# Analysis: Completed model\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _run(self, bundle: dict[str, str]) -> subprocess.CompletedProcess[str]:
        bundle_path = self.root / "bundle.json"
        bundle_path.write_text(json.dumps(bundle, ensure_ascii=False), encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                str(RESEARCH_DB),
                "--project",
                str(self.root),
                "migrate-human-artifact-path",
                str(bundle_path),
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_cli_migrates_dataset_to_contract_path_without_changing_identity(self) -> None:
        result = self._run(
            {
                "entity_type": "dataset",
                "slug": "sample",
                "new_path": "data/sample/README.md",
                "reason": "Adopt the canonical human-artifact contract path.",
            }
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        with sqlite3.connect(database_path(self.root)) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT * FROM datasets WHERE slug='sample'"
            ).fetchone()
            assert row is not None
            self.assertEqual(row["provenance_path"], "data/sample/README.md")
            self.assertEqual(row["identity"], "sha256:sample")
            self.assertEqual(row["version"], "v1")
            change = connection.execute(
                """
                SELECT action, reason FROM change_log
                WHERE entity_type='dataset' AND entity_id=?
                ORDER BY id DESC LIMIT 1
                """,
                (str(row["id"]),),
            ).fetchone()
            assert change is not None
            self.assertEqual(change["action"], "human_artifact_path_migrated")
            self.assertIn("canonical human-artifact contract path", change["reason"])

    def test_cli_migrates_completed_analysis_without_reopening_scientific_fields(self) -> None:
        result = self._run(
            {
                "entity_type": "analysis",
                "slug": "model",
                "new_path": "analysis/model/README.md",
                "reason": "Adopt the canonical human-artifact contract path.",
            }
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        with sqlite3.connect(database_path(self.root)) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT * FROM analysis_runs WHERE slug='model'"
            ).fetchone()
            assert row is not None
            self.assertEqual(row["analysis_path"], "analysis/model/README.md")
            self.assertEqual(row["status"], "completed")
            self.assertEqual(row["estimand"], "Descriptive audit result")
            self.assertEqual(row["primary_analysis"], "Fixed audit procedure")

    def test_cli_rejects_noncanonical_target_path(self) -> None:
        wrong = self.root / "data" / "wrong" / "README.md"
        wrong.parent.mkdir(parents=True)
        wrong.write_text("# Dataset: Wrong\n", encoding="utf-8")

        result = self._run(
            {
                "entity_type": "dataset",
                "slug": "sample",
                "new_path": "data/wrong/README.md",
                "reason": "Try a wrong path.",
            }
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("data/sample/README.md", result.stdout)

        with sqlite3.connect(database_path(self.root)) as connection:
            path = connection.execute(
                "SELECT provenance_path FROM datasets WHERE slug='sample'"
            ).fetchone()[0]
        self.assertEqual(path, "data/legacy-sample.md")


if __name__ == "__main__":
    unittest.main()

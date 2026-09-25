from __future__ import annotations

import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from research_db_core import database_path, init_database  # noqa: E402
from research_db_ops.completion import literature_completion_readiness  # noqa: E402
from research_db_ops.downstream import list_datasets, record_dataset  # noqa: E402


class DatasetPaperMembershipTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "RESEARCH.md").write_text(
            "# Research\n\n## Objective\n\n验证论文样本数据集的来源追踪。\n",
            encoding="utf-8",
        )
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
        data_dir = self.root / "data" / "paper-sample"
        data_dir.mkdir(parents=True)
        (data_dir / "README.md").write_text("# Dataset: Paper sample\n", encoding="utf-8")
        (data_dir / "sample.tsv").write_text("paper_id\nP000001\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _insert_unreviewed_paper(self, paper_id: str = "P000001") -> None:
        now = "2026-09-25T00:00:00+00:00"
        with closing(sqlite3.connect(database_path(self.root))) as connection, connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO papers(
                    id, title, status, read_depth, reading_status, critical_status,
                    created_at, updated_at
                ) VALUES (?, 'Systematic corpus paper', 'active', 'full_scan',
                          'unread', 'not_reviewed', ?, ?)
                """,
                (paper_id, now, now),
            )
            connection.execute(
                """
                INSERT INTO acquisition_attempts(
                    paper_id, target_kind, route_family, resource_kind, source_url,
                    outcome, detail, attempted_at, access_basis, access_basis_detail
                ) VALUES (?, 'main_text', 'repository', 'xml',
                          'https://repository.example/paper', 'acquired',
                          'Verified repository full text.', ?, 'public_repository',
                          'Public repository full text verified for test.')
                """,
                (paper_id, now),
            )

    def _record_dataset(self) -> None:
        record_dataset(
            self.root,
            {
                "slug": "paper-sample",
                "title": "Paper sample",
                "identity": "test:paper-sample",
                "source": "systematic literature frame",
                "received_at": "2026-09-25T00:00:00+00:00",
                "unit_of_inference": "paper",
                "provenance_path": "data/paper-sample/README.md",
                "paper_ids": ["P000001"],
                "artifacts": [
                    {
                        "role": "curated",
                        "location": "data/paper-sample/sample.tsv",
                    }
                ],
            },
        )

    def test_record_dataset_round_trips_paper_membership(self) -> None:
        self._insert_unreviewed_paper()
        self._record_dataset()

        dataset = list_datasets(self.root)["datasets"][0]
        self.assertEqual(dataset["paper_ids"], ["P000001"])

    def test_dataset_member_without_candidate_is_not_direct_literature_target(self) -> None:
        self._insert_unreviewed_paper()
        self._record_dataset()

        result = literature_completion_readiness(
            self.root, {"relevant_candidate_count": 0}
        )
        targeted = [
            item
            for item in result["blockers"]
            if item["reason"] == "targeted_paper_not_fully_reviewed"
        ]
        self.assertEqual(targeted, [])


if __name__ == "__main__":
    unittest.main()

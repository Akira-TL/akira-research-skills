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


class LiteratureDeferredCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "RESEARCH.md").write_text(
            "# Research\n\n## Objective\n\n测试文献延期门禁。\n",
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

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _insert_unreviewed_acquired_candidate(
        self,
        *,
        candidate_id: int,
        paper_id: str,
        priority: str,
        defer_reason: str | None,
    ) -> None:
        now = "2026-09-25T00:00:00+00:00"
        with closing(sqlite3.connect(database_path(self.root))) as connection, connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO papers(
                    id, title, status, read_depth, reading_status, critical_status,
                    created_at, updated_at
                ) VALUES (?, ?, 'active', 'full_scan', 'unread', 'not_reviewed', ?, ?)
                """,
                (paper_id, f"Paper {paper_id}", now, now),
            )
            connection.execute(
                """
                INSERT INTO candidates(
                    id, title, identity_status, relevance_status, paper_id,
                    created_at, updated_at, acquisition_status, reading_priority,
                    defer_reason
                ) VALUES (?, ?, 'resolved', 'relevant', ?, ?, ?, 'acquired', ?, ?)
                """,
                (
                    candidate_id,
                    f"Candidate {candidate_id}",
                    paper_id,
                    now,
                    now,
                    priority,
                    defer_reason,
                ),
            )
            connection.execute(
                """
                INSERT INTO acquisition_attempts(
                    candidate_id, target_kind, route_family, resource_kind, source_url,
                    outcome, detail, attempted_at, access_basis, access_basis_detail
                ) VALUES (?, 'main_text', 'publisher', 'full_text_html', ?,
                          'acquired', 'Verified publisher full text.', ?,
                          'publisher_open', 'Publisher-hosted open full text verified for test.')
                """,
                (candidate_id, f"https://publisher.example/{candidate_id}", now),
            )

    def test_normal_candidate_with_defer_reason_does_not_block_literature_review(self) -> None:
        self._insert_unreviewed_acquired_candidate(
            candidate_id=1,
            paper_id="P000001",
            priority="normal",
            defer_reason="Historical branch is resolved; retain relevance for future reuse.",
        )

        result = literature_completion_readiness(
            self.root, {"relevant_candidate_count": 1}
        )
        blockers = [
            item
            for item in result["blockers"]
            if item.get("candidate_id") == 1
            and item["reason"] == "relevant_acquired_not_fully_reviewed"
        ]
        self.assertEqual(blockers, [])

    def test_high_candidate_cannot_use_defer_reason_to_skip_review(self) -> None:
        self._insert_unreviewed_acquired_candidate(
            candidate_id=1,
            paper_id="P000001",
            priority="high",
            defer_reason="This text must not close a high-priority candidate.",
        )

        result = literature_completion_readiness(
            self.root, {"relevant_candidate_count": 1}
        )
        blockers = [
            item
            for item in result["blockers"]
            if item.get("candidate_id") == 1
            and item["reason"] == "relevant_acquired_not_fully_reviewed"
        ]
        self.assertEqual(len(blockers), 1)


if __name__ == "__main__":
    unittest.main()

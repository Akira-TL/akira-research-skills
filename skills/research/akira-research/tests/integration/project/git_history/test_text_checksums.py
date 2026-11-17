from __future__ import annotations

import hashlib
import sqlite3
import sys
import unittest
from contextlib import closing
from pathlib import Path

FIXTURE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIXTURE_DIR))

from git_fixtures import GitResearchProject  # noqa: E402

from research_db_ops.downstream import record_dataset  # noqa: E402
from research_db_ops.project import redact_text_checksums  # noqa: E402
from research_db_ops.project.text_checksums import TEXT_CHECKSUM_PLACEHOLDER  # noqa: E402

DIGEST = hashlib.sha256(b"result").hexdigest()
OTHER = hashlib.sha256(b"manifest").hexdigest()
COMMIT = hashlib.sha1(b"commit").hexdigest()
NOW = "2026-11-17T00:00:00+00:00"


class RedactTextChecksumsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = GitResearchProject()
        self.root = self.project.root
        self.db = self.root / ".research" / "research.sqlite"
        self.project.write("data/run/README.md", "# 来源\n\n运行输出。\n")
        self.project.write("data/run/notes.md", "说明\n")
        self.weights = self.project.write("data/run/model.bin", "weights\n")
        self.weights_digest = hashlib.sha256(self.weights.read_bytes()).hexdigest()
        record_dataset(
            self.root,
            {
                "slug": "run",
                "title": "Run outputs",
                "identity": f"run:result-{DIGEST}",
                "source": "test fixture",
                "received_at": NOW,
                "unit_of_inference": "run",
                "provenance_path": "data/run/README.md",
                "artifacts": [
                    {
                        "role": "metadata",
                        "location": "data/run/notes.md",
                        "version": f"session-00-journal-{DIGEST}",
                        "tracking_reason": f"保留于冻结提交{COMMIT}，SHA-256为{DIGEST}。",
                    },
                    {
                        "role": "raw",
                        "location": "data/run/model.bin",
                        "git_tracking": "not_required",
                        "tracking_reason": "large checkpoint kept outside Git",
                        "sha256": self.weights_digest,
                    },
                ],
            },
        )
        with closing(sqlite3.connect(self.db)) as connection:
            connection.execute(
                "INSERT INTO path_migrations(migration_commit, old_prefix, new_prefix, reason, created_at)"
                " VALUES (?, 'a/', 'b/', ?, ?)",
                (COMMIT, f"迁移提交 {COMMIT} 不变；manifest sha256:{OTHER.upper()}；结果SHA={DIGEST}。", NOW),
            )
            connection.execute(
                "INSERT INTO freeze_revisions(path, revision_commit, category, reason, created_at)"
                " VALUES ('data/run/notes.md', ?, 'redundant_checksum_removal', ?, ?)",
                (COMMIT, f"去掉 {DIGEST}；更长的 {DIGEST}{COMMIT} 与标识 x{DIGEST} 不算独立值。", NOW),
            )
            connection.commit()

    def tearDown(self) -> None:
        self.project.cleanup()

    def _notes_reason(self) -> str:
        return self._cell("SELECT tracking_reason FROM dataset_artifacts WHERE location = 'data/run/notes.md'")

    def _cell(self, query: str) -> str:
        with closing(sqlite3.connect(self.db)) as connection:
            return connection.execute(query).fetchone()[0]

    def _logged(self) -> list[tuple[str, str, str]]:
        with closing(sqlite3.connect(self.db)) as connection:
            return connection.execute(
                "SELECT entity_type, reason, summary FROM change_log"
                " WHERE action = 'text_checksum_redacted' ORDER BY id"
            ).fetchall()

    def test_dry_run_lists_cells_without_writing(self) -> None:
        preview = redact_text_checksums(self.root, dry_run=True)
        self.assertTrue(preview["dry_run"])
        self.assertEqual(preview["cell_count"], 3)
        self.assertEqual(preview["checksum_count"], 4)
        self.assertEqual(
            preview["counts"],
            {
                "dataset_artifacts.tracking_reason": 1,
                "freeze_revisions.reason": 1,
                "path_migrations.reason": 2,
            },
        )
        self.assertIn(DIGEST, self._notes_reason())
        self.assertEqual(self._logged(), [])

    def test_redacts_prose_across_tables_and_keeps_commit_ids(self) -> None:
        result = redact_text_checksums(self.root, reason="清理自由文本校验值。")
        self.assertEqual(result["cell_count"], 3)
        self.assertEqual(
            self._notes_reason(),
            f"保留于冻结提交{COMMIT}，SHA-256为{TEXT_CHECKSUM_PLACEHOLDER}。",
        )
        self.assertEqual(
            self._cell("SELECT reason FROM path_migrations"),
            f"迁移提交 {COMMIT} 不变；manifest {TEXT_CHECKSUM_PLACEHOLDER}；结果SHA={TEXT_CHECKSUM_PLACEHOLDER}。",
        )
        self.assertEqual(
            self._cell("SELECT reason FROM freeze_revisions"),
            f"去掉 {TEXT_CHECKSUM_PLACEHOLDER}；更长的 {DIGEST}{COMMIT} 与标识 x{DIGEST} 不算独立值。",
        )
        # identity, version, dedicated sha256 and commit columns stay as recorded
        self.assertEqual(self._cell("SELECT identity FROM datasets"), f"run:result-{DIGEST}")
        self.assertEqual(
            self._cell("SELECT version FROM dataset_artifacts WHERE location = 'data/run/notes.md'"),
            f"session-00-journal-{DIGEST}",
        )
        self.assertEqual(
            self._cell("SELECT sha256 FROM dataset_artifacts WHERE location = 'data/run/model.bin'"),
            self.weights_digest,
        )
        self.assertEqual(self._cell("SELECT migration_commit FROM path_migrations"), COMMIT)

        logged = self._logged()
        self.assertEqual(
            [row[0] for row in logged], ["dataset_artifacts", "freeze_revisions", "path_migrations"]
        )
        self.assertTrue(all(row[1] == "清理自由文本校验值。" for row in logged))
        self.assertIn(f"column=reason; old_values=sha256:{OTHER.upper()}, {DIGEST}", logged[2][2])

        again = redact_text_checksums(self.root)
        self.assertEqual(again["cell_count"], 0)
        self.assertEqual(len(self._logged()), 3)


if __name__ == "__main__":
    unittest.main()

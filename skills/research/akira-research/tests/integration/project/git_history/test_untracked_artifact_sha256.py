from __future__ import annotations

import hashlib
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

FIXTURE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIXTURE_DIR))

from git_fixtures import GitResearchProject  # noqa: E402

from research_db_core import ResearchDbError, apply_migrations, validate  # noqa: E402
from research_db_ops.downstream import list_datasets, record_dataset  # noqa: E402
from research_db_support.schema import list_migrations  # noqa: E402


def _dataset_bundle(artifact: dict) -> dict:
    return {
        "slug": "weights",
        "title": "Model checkpoint",
        "identity": "example:weights",
        "source": "test fixture",
        "received_at": "2026-08-28T00:00:00+00:00",
        "unit_of_inference": "model",
        "provenance_path": "data/weights/README.md",
        "artifacts": [artifact],
    }


class UntrackedArtifactSha256Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = GitResearchProject()
        self.root = self.project.root
        self.project.write("data/weights/README.md", "# 检查点来源\n\n模型权重。\n")
        self.weights = self.project.write("data/weights/model.bin", "weights-v1\n")
        self.digest = hashlib.sha256(self.weights.read_bytes()).hexdigest()

    def tearDown(self) -> None:
        self.project.cleanup()

    def test_git_tracked_artifact_rejects_checksum(self) -> None:
        with self.assertRaisesRegex(ResearchDbError, "提交号 \\+ 路径"):
            record_dataset(
                self.root,
                _dataset_bundle(
                    {"role": "raw", "location": "data/weights/model.bin", "sha256": self.digest}
                ),
            )

    def test_untracked_local_artifact_records_verified_checksum(self) -> None:
        untracked = {
            "role": "raw",
            "location": "data/weights/model.bin",
            "git_tracking": "not_required",
            "tracking_reason": "large checkpoint kept outside Git",
        }
        with self.assertRaisesRegex(ResearchDbError, "不一致"):
            record_dataset(self.root, _dataset_bundle({**untracked, "sha256": "0" * 64}))

        record_dataset(self.root, _dataset_bundle({**untracked, "sha256": f"sha256:{self.digest.upper()}"}))
        artifact = list_datasets(self.root)["datasets"][0]["artifacts"][0]
        self.assertEqual(artifact["sha256"], self.digest)
        self.assertTrue(validate(self.root)["ok"], validate(self.root)["errors"])

    def test_external_artifact_records_checksum_without_local_file(self) -> None:
        external = {
            "role": "raw",
            "location": "s3://bucket/checkpoint-34600.pt",
            "storage_kind": "external",
            "git_tracking": "not_required",
            "tracking_reason": "remote checkpoint",
        }
        record_dataset(self.root, _dataset_bundle(external))
        record_dataset(self.root, _dataset_bundle({**external, "sha256": "a" * 64}))
        artifact = list_datasets(self.root)["datasets"][0]["artifacts"][0]
        self.assertEqual(artifact["sha256"], "a" * 64)
        with self.assertRaisesRegex(ResearchDbError, "不可静默改写"):
            record_dataset(self.root, _dataset_bundle({**external, "sha256": "b" * 64}))


class Sha256MigrationTests(unittest.TestCase):
    def test_migration_moves_untracked_version_checksums_only(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            db_path = Path(tempdir) / "research.sqlite"
            with closing(sqlite3.connect(db_path)) as connection, connection:
                for migration in list_migrations():
                    if migration.version > 29:
                        break
                    connection.executescript(migration.path.read_text(encoding="utf-8"))
                    connection.execute(f"PRAGMA user_version = {migration.version}")
                connection.execute(
                    "INSERT INTO meta(key, value) VALUES('schema_version', '29') "
                    "ON CONFLICT(key) DO UPDATE SET value = excluded.value"
                )
                connection.execute(
                    """
                    INSERT INTO datasets(slug, title, identity, source, received_at, unit_of_inference,
                                         provenance_path, status, created_at, updated_at)
                    VALUES ('d', 'D', 'i', 's', '2026-01-01T00:00:00+00:00', 'u', 'data/d/README.md',
                            'active', '2026-01-01T00:00:00+00:00', '2026-01-01T00:00:00+00:00')
                    """
                )
                rows = [
                    ("data/d/tracked.json", "required", "sha256:" + "b" * 64),
                    ("data/d/untracked.bin", "not_required", "sha256:" + "C" * 64),
                    ("data/d/bare.bin", "not_required", "d" * 64),
                    ("data/d/run.bin", "not_required", "run-2b6065c"),
                ]
                for location, tracking, version in rows:
                    connection.execute(
                        """
                        INSERT INTO dataset_artifacts(dataset_id, role, location, storage_kind, git_tracking,
                                                      tracking_reason, version, created_at)
                        VALUES (1, 'raw', ?, 'local', ?, 'r', ?, '2026-01-01T00:00:00+00:00')
                        """,
                        (location, tracking, version),
                    )
            applied = apply_migrations(db_path)
            self.assertIn(30, applied)
            with closing(sqlite3.connect(db_path)) as connection:
                values = dict(
                    connection.execute("SELECT location, sha256 FROM dataset_artifacts").fetchall()
                )
                versions = [row[0] for row in connection.execute("SELECT version FROM dataset_artifacts")]
        self.assertIsNone(values["data/d/tracked.json"])
        self.assertEqual(values["data/d/untracked.bin"], "c" * 64)
        self.assertEqual(values["data/d/bare.bin"], "d" * 64)
        self.assertIsNone(values["data/d/run.bin"])
        self.assertIn("sha256:" + "b" * 64, versions)


if __name__ == "__main__":
    unittest.main()

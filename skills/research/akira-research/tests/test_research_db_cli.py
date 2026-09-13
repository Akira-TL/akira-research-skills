from __future__ import annotations

from contextlib import closing, redirect_stdout
import io
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from research_db import _load_json_object, build_parser, bundle_path, cmd_migrate  # noqa: E402
from research_db_core import database_path, init_database  # noqa: E402
from research_db_support.schema import (  # noqa: E402
    LITERATURE_HUMAN_FORMAT_LEGACY_BASELINE_META_KEY,
    list_migrations,
)


class ResearchDbCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "RESEARCH.md").write_text("# Research\n", encoding="utf-8")
        init_database(self.root)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_bundle_defaults_live_under_research_directory(self) -> None:
        expected = self.root / ".research" / "bundles" / "reconstruction.json"
        expected.write_text(json.dumps({"paper_id": "P000001"}), encoding="utf-8")

        self.assertEqual(bundle_path(self.root, "ingest-reading", None), expected)
        self.assertEqual(
            _load_json_object(self.root, "ingest-reading", None),
            {"paper_id": "P000001"},
        )
        self.assertEqual(
            bundle_path(self.root, "add-paper-artifacts", None),
            self.root / ".research" / "bundles" / "paper-artifacts.json",
        )

    def test_explicit_relative_bundle_path_is_project_relative(self) -> None:
        custom = self.root / ".research" / "bundles" / "custom.json"
        custom.write_text(json.dumps({"ok": True}), encoding="utf-8")

        self.assertEqual(
            bundle_path(self.root, "ingest-reading", ".research/bundles/custom.json"),
            custom,
        )

    def test_bundle_argument_is_optional(self) -> None:
        args = build_parser().parse_args(
            ["--project", str(self.root), "ingest-critical"]
        )
        self.assertIsNone(args.bundle)

        search_args = build_parser().parse_args(
            ["--project", str(self.root), "record-search"]
        )
        self.assertIsNone(search_args.bundle)

        artifact_args = build_parser().parse_args(
            ["--project", str(self.root), "add-paper-artifacts"]
        )
        self.assertIsNone(artifact_args.bundle)

    def test_read_query_commands_are_exposed(self) -> None:
        search_args = build_parser().parse_args(
            ["--project", str(self.root), "search", "Blautia", "--entity-type", "claim"]
        )
        self.assertEqual(search_args.entity_type, ["claim"])

        issue_args = build_parser().parse_args(
            [
                "--project",
                str(self.root),
                "issues",
                "--paper",
                "P000001",
                "--severity",
                "major",
            ]
        )
        self.assertEqual(issue_args.paper, "P000001")
        self.assertEqual(issue_args.severity, "major")

        related_args = build_parser().parse_args(
            ["--project", str(self.root), "related", "P000001"]
        )
        self.assertEqual(related_args.paper_id, "P000001")

        relate_args = build_parser().parse_args(
            ["--project", str(self.root), "relate"]
        )
        self.assertIsNone(relate_args.bundle)

    def test_completion_and_discovery_commands_are_exposed(self) -> None:
        validate_args = build_parser().parse_args(
            ["--project", str(self.root), "validate", "--completion"]
        )
        self.assertTrue(validate_args.completion)

        discovery_args = build_parser().parse_args(
            ["--project", str(self.root), "discovery-status"]
        )
        self.assertEqual(discovery_args.command, "discovery-status")

        merge_args = build_parser().parse_args(
            [
                "--project",
                str(self.root),
                "merge-candidates",
                "1",
                "2",
                "--reason",
                "same DOI",
            ]
        )
        self.assertEqual(merge_args.keep_id, 1)
        self.assertEqual(merge_args.merge_id, 2)

        dataset_args = build_parser().parse_args(
            ["--project", str(self.root), "record-dataset"]
        )
        self.assertIsNone(dataset_args.bundle)
        analysis_args = build_parser().parse_args(
            ["--project", str(self.root), "record-analysis"]
        )
        self.assertIsNone(analysis_args.bundle)
        research_node_args = build_parser().parse_args(
            ["--project", str(self.root), "record-research-node"]
        )
        self.assertIsNone(research_node_args.bundle)
        research_edge_args = build_parser().parse_args(
            ["--project", str(self.root), "record-research-edge"]
        )
        self.assertIsNone(research_edge_args.bundle)
        tree_state_args = build_parser().parse_args(
            ["--project", str(self.root), "set-research-tree-state"]
        )
        self.assertIsNone(tree_state_args.bundle)
        study_args = build_parser().parse_args(
            ["--project", str(self.root), "record-study"]
        )
        self.assertIsNone(study_args.bundle)
        self.assertEqual(
            build_parser().parse_args(["--project", str(self.root), "datasets"]).command,
            "datasets",
        )
        self.assertEqual(
            build_parser().parse_args(["--project", str(self.root), "analyses"]).command,
            "analyses",
        )
        self.assertEqual(
            build_parser().parse_args(["--project", str(self.root), "research-tree"]).command,
            "research-tree",
        )
        self.assertEqual(
            build_parser().parse_args(["--project", str(self.root), "studies"]).command,
            "studies",
        )
        hypothesis_args = build_parser().parse_args(
            ["--project", str(self.root), "record-hypothesis-set"]
        )
        self.assertIsNone(hypothesis_args.bundle)
        design_args = build_parser().parse_args(
            ["--project", str(self.root), "record-design"]
        )
        self.assertIsNone(design_args.bundle)
        evaluation_args = build_parser().parse_args(
            ["--project", str(self.root), "record-hypothesis-evaluation"]
        )
        self.assertIsNone(evaluation_args.bundle)
        self.assertEqual(
            build_parser().parse_args(["--project", str(self.root), "hypothesis-sets"]).command,
            "hypothesis-sets",
        )
        self.assertEqual(
            build_parser().parse_args(["--project", str(self.root), "designs"]).command,
            "designs",
        )
        self.assertEqual(
            build_parser().parse_args(
                ["--project", str(self.root), "hypothesis-evaluations"]
            ).command,
            "hypothesis-evaluations",
        )
        communication_args = build_parser().parse_args(
            ["--project", str(self.root), "record-communication"]
        )
        self.assertIsNone(communication_args.bundle)
        journal_args = build_parser().parse_args(
            ["--project", str(self.root), "record-journal"]
        )
        self.assertIsNone(journal_args.bundle)
        target_args = build_parser().parse_args(
            ["--project", str(self.root), "record-target-workspace"]
        )
        self.assertIsNone(target_args.bundle)
        relocation_args = build_parser().parse_args(
            ["--project", str(self.root), "relocate-communication-artifact"]
        )
        self.assertIsNone(relocation_args.bundle)
        self.assertEqual(
            bundle_path(self.root, "record-journal", None),
            self.root / ".research" / "bundles" / "communication-journal.json",
        )
        self.assertEqual(
            bundle_path(self.root, "record-target-workspace", None),
            self.root / ".research" / "bundles" / "communication-target-workspace.json",
        )
        self.assertEqual(
            bundle_path(self.root, "relocate-communication-artifact", None),
            self.root / ".research" / "bundles" / "communication-artifact-relocation.json",
        )
        self.assertEqual(
            build_parser().parse_args(["--project", str(self.root), "communications"]).command,
            "communications",
        )

    def test_migrate_to_literature_contract_records_baseline_and_rewrites_marker(self) -> None:
        legacy_root = self.root / "legacy-literature"
        legacy_root.mkdir()
        (legacy_root / "RESEARCH.md").write_text("# Research\n", encoding="utf-8")
        papers = legacy_root / "literature" / "papers"
        papers.mkdir(parents=True)
        note_path = papers / "Paper title - Wang - 2026.md"
        historical = (
            "# Paper title\n\n"
            "<!-- akira:literature-note:v1 -->\n\n"
            "用户笔记和正文必须原样保留。\n"
        )
        note_path.write_text(historical, encoding="utf-8")

        db_path = database_path(legacy_root)
        db_path.parent.mkdir(parents=True)
        with closing(sqlite3.connect(db_path)) as connection, connection:
            for migration in list_migrations():
                if migration.version >= 25:
                    break
                connection.executescript(migration.path.read_text(encoding="utf-8"))
                connection.execute(f"PRAGMA user_version = {migration.version}")
                connection.execute(
                    """
                    INSERT INTO meta(key, value) VALUES('schema_version', ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                    """,
                    (str(migration.version),),
                )

        subprocess.run(["git", "init", str(legacy_root)], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", str(legacy_root), "config", "user.email", "research@example.test"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(legacy_root), "config", "user.name", "Research Test"],
            check=True,
        )
        subprocess.run(["git", "-C", str(legacy_root), "add", "-A"], check=True)
        subprocess.run(
            ["git", "-C", str(legacy_root), "commit", "-m", "RESEARCH: legacy literature"],
            check=True,
            capture_output=True,
        )
        baseline = subprocess.run(
            ["git", "-C", str(legacy_root), "rev-parse", "HEAD"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()

        args = build_parser().parse_args(["--project", str(legacy_root), "migrate"])
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(cmd_migrate(args), 0)
        payload = json.loads(stdout.getvalue())

        self.assertEqual(payload["applied_migrations"], [25, 26])
        self.assertEqual(payload["literature_human_format_legacy_baseline_commit"], baseline)
        self.assertEqual(
            payload["literature_marker_migration"]["migrated_paths"],
            ["literature/papers/Paper title - Wang - 2026.md"],
        )
        migrated = note_path.read_text(encoding="utf-8")
        self.assertIn("<!-- akira:literature-note -->", migrated)
        self.assertNotIn("<!-- akira:literature-note:v1 -->", migrated)
        self.assertIn("用户笔记和正文必须原样保留。", migrated)
        with closing(sqlite3.connect(db_path)) as connection:
            self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], 26)
            stored = connection.execute(
                "SELECT value FROM meta WHERE key = ?",
                (LITERATURE_HUMAN_FORMAT_LEGACY_BASELINE_META_KEY,),
            ).fetchone()
        self.assertEqual(stored[0], baseline)

    def test_candidate_queue_filters_are_exposed(self) -> None:
        args = build_parser().parse_args(
            [
                "--project",
                str(self.root),
                "candidates",
                "--relevance",
                "relevant",
                "--acquisition",
                "queued",
                "--priority",
                "core",
            ]
        )
        self.assertEqual(args.relevance, "relevant")
        self.assertEqual(args.acquisition, "queued")
        self.assertEqual(args.priority, "core")


if __name__ == "__main__":
    unittest.main()

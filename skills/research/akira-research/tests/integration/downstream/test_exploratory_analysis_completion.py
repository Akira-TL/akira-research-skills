from __future__ import annotations

import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[3] / "scripts"
MIGRATION_DIR = SCRIPT_DIR.parent / "migrations" / "versions"
sys.path.insert(0, str(SCRIPT_DIR))

from research_db_core import init_database  # noqa: E402
from research_db_ops.completion import validate_completion  # noqa: E402
from research_db_ops.downstream import (  # noqa: E402
    list_analyses,
    record_analysis,
    record_analysis_attempt,
    record_dataset,
)


class ExploratoryAnalysisCompletionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "RESEARCH.md").write_text(
            """# Research

## Objective

验证探索性综合与确认性估计使用不同的完成门禁。

## Applicable Standards

不适用：当前没有额外正式规范。

## Current Loop

ANALYSIS

## Active Uncertainty

探索性综合是否可以在不伪造新估计量的情况下完成？

## Current State

测试项目登记一个数据集和一个分析。

## Active Work

验证分析完成门禁的来源追踪规则。

## Open Threads

暂无。

## Key Decisions

确认性分析需要主要估计结果；探索性综合可以只产生表格结果。

## Navigation

不适用。

## References

- `.research/research.sqlite`
""",
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
        self._write_assets()
        self._record_dataset()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _write_assets(self) -> None:
        (self.root / "data" / "sleep-data").mkdir(parents=True)
        (self.root / "analysis" / "sleep-trajectory").mkdir(parents=True)
        (self.root / "scripts" / "analyses").mkdir(parents=True)

        (self.root / "data" / "sleep-data" / "README.md").write_text(
            """# Dataset: Sleep repeated measures

## Navigation

- [Research](../../RESEARCH.md)

## Dataset Identity

测试用数据集。

## Research Purpose

支持分析完成门禁测试。

## Source and Version

固定测试数据。

## Population and Sample Mapping

行级结果用于测试。

## Data Layers and Artifacts

原始 CSV 为输入。

## Metadata / Missingness / Exclusions

不适用。

## QC and Anomalies

不适用。

## Processing and Reproduction

由测试分析脚本读取。

## Freeze / Access / Ethics

本地测试数据，无访问限制。
""",
            encoding="utf-8",
        )
        (self.root / "data" / "sleep-data" / "raw.csv").write_text(
            "id,value\n1,2\n2,3\n", encoding="utf-8"
        )
        (self.root / "data" / "README.md").write_text(
            "# Data\n\n## Objects\n\n"
            "- [Sleep repeated measures](sleep-data/README.md) — 测试数据集。\n\n"
            "## Relations\n\n"
            "- [Sleep repeated measures](sleep-data/README.md) → "
            "[Sleep trajectory analysis](../analysis/sleep-trajectory/README.md)\n",
            encoding="utf-8",
        )
        (self.root / "analysis" / "sleep-trajectory" / "README.md").write_text(
            """# Analysis: Sleep trajectory analysis

## Navigation

- [Research](../../RESEARCH.md)
- [数据集](../../data/sleep-data/README.md)

## Question / Target Contrast

验证不同分析模式的完成要求。

## Inputs and Data Freeze

使用已登记测试数据。

## Unit of Inference

结果行。

## Primary Analysis

按测试分支执行确认性估计或探索性综合。

## Exploratory / Sensitivity Analyses

由具体测试定义。

## Assumptions and Diagnostics

不适用。

## Outputs

输出表或诊断文件。

## Reproduction

入口为 `scripts/analyses/trajectory.py`。

## Result Boundary

仅验证来源追踪门禁。

## Amendments

不适用。
""",
            encoding="utf-8",
        )
        (self.root / "analysis" / "README.md").write_text(
            "# Analyses\n\n## Objects\n\n"
            "- [Sleep trajectory analysis](sleep-trajectory/README.md) — 测试分析。\n\n"
            "## Relations\n\n"
            "- [Sleep trajectory analysis](sleep-trajectory/README.md) → "
            "[Sleep repeated measures](../data/sleep-data/README.md)\n",
            encoding="utf-8",
        )
        (self.root / "scripts" / "analyses" / "trajectory.py").write_text(
            "print('analysis')\n", encoding="utf-8"
        )

    def _record_dataset(self) -> None:
        record_dataset(
            self.root,
            {
                "slug": "sleep-data",
                "title": "Sleep repeated measures",
                "identity": "example:sleep",
                "source": "test fixture",
                "received_at": "2026-08-28T00:00:00+00:00",
                "unit_of_inference": "result row",
                "provenance_path": "data/sleep-data/README.md",
                "artifacts": [
                    {"role": "raw", "location": "data/sleep-data/raw.csv"}
                ],
            },
        )

    def _record_planned_analysis(self, mode: str) -> None:
        estimand = (
            "Population-average change per study day"
            if mode == "confirmatory"
            else "No new estimand; organize existing results without re-estimation."
        )
        record_analysis(
            self.root,
            {
                "slug": "sleep-trajectory",
                "title": "Sleep trajectory analysis",
                "analysis_mode": mode,
                "status": "planned",
                "target_uncertainty": "Does this analysis satisfy its mode-specific completion contract?",
                "estimand": estimand,
                "unit_of_inference": "result row",
                "primary_analysis": "Mode-specific deterministic test analysis.",
                "analysis_path": "analysis/sleep-trajectory/README.md",
                "code_path": "scripts/analyses/trajectory.py",
                "dataset_slugs": ["sleep-data"],
            },
        )

    def _select_attempt(self, commit: str) -> None:
        record_analysis_attempt(
            self.root,
            {
                "analysis_slug": "sleep-trajectory",
                "attempt_key": "A001",
                "status": "selected",
                "git_commit": commit,
                "reason": "Primary executable specification for the completion-gate test.",
                "decision_reason": "This is the only execution used by the test.",
            },
        )

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

    def test_completed_exploratory_synthesis_can_finish_without_estimate_artifact(self) -> None:
        self._record_planned_analysis("exploratory")
        execution_commit = self._commit("ANALYSIS: record exploratory synthesis plan")
        self._select_attempt(execution_commit)

        outputs = self.root / "analysis" / "sleep-trajectory" / "outputs"
        outputs.mkdir()
        summary_path = outputs / "summary.csv"
        summary_path.write_text("category,count\nkept,2\n", encoding="utf-8")
        completed_at = list_analyses(self.root)["analyses"][0]["started_at"]

        record_analysis(
            self.root,
            {
                "slug": "sleep-trajectory",
                "title": "Sleep trajectory analysis",
                "analysis_mode": "exploratory",
                "status": "completed",
                "target_uncertainty": "Does this analysis satisfy its mode-specific completion contract?",
                "estimand": "No new estimand; organize existing results without re-estimation.",
                "unit_of_inference": "result row",
                "primary_analysis": "Mode-specific deterministic test analysis.",
                "analysis_path": "analysis/sleep-trajectory/README.md",
                "code_path": "scripts/analyses/trajectory.py",
                "dataset_slugs": ["sleep-data"],
                "completed_at": completed_at,
                "artifacts": [
                    {"role": "table", "path": "analysis/sleep-trajectory/outputs/summary.csv"}
                ],
                "observations": [
                    {
                        "statement": "The synthesis retained two result rows.",
                        "source_path": "analysis/sleep-trajectory/outputs/summary.csv",
                        "source_locator": "row kept",
                    }
                ],
            },
        )
        self._commit("ANALYSIS: record exploratory synthesis result")

        result = validate_completion(self.root)
        self.assertTrue(result["downstream"]["ready"], result["downstream"]["blockers"])

    def test_completed_confirmatory_analysis_still_requires_estimate_artifact(self) -> None:
        self._record_planned_analysis("confirmatory")
        freeze_commit = self._commit("ANALYSIS: freeze confirmatory plan")
        self._select_attempt(freeze_commit)

        outputs = self.root / "analysis" / "sleep-trajectory" / "outputs"
        outputs.mkdir()
        diagnostic_path = outputs / "diagnostic.txt"
        diagnostic_path.write_text("converged=true\n", encoding="utf-8")
        completed_at = list_analyses(self.root)["analyses"][0]["started_at"]

        record_analysis(
            self.root,
            {
                "slug": "sleep-trajectory",
                "title": "Sleep trajectory analysis",
                "analysis_mode": "confirmatory",
                "status": "completed",
                "target_uncertainty": "Does this analysis satisfy its mode-specific completion contract?",
                "estimand": "Population-average change per study day",
                "unit_of_inference": "result row",
                "primary_analysis": "Mode-specific deterministic test analysis.",
                "analysis_path": "analysis/sleep-trajectory/README.md",
                "code_path": "scripts/analyses/trajectory.py",
                "dataset_slugs": ["sleep-data"],
                "freeze_commit": freeze_commit,
                "completed_at": completed_at,
                "artifacts": [
                    {
                        "role": "diagnostic",
                        "path": "analysis/sleep-trajectory/outputs/diagnostic.txt",
                    }
                ],
                "observations": [
                    {
                        "statement": "The model converged.",
                        "source_path": "analysis/sleep-trajectory/outputs/diagnostic.txt",
                        "source_locator": "converged",
                    }
                ],
            },
        )
        self._commit("ANALYSIS: record diagnostic-only confirmatory result")

        result = validate_completion(self.root)
        reasons = {item["reason"] for item in result["downstream"]["blockers"]}
        self.assertIn("completed_analysis_missing_estimate_artifact", reasons)
    def test_migration_grandfathers_unchanged_legacy_downstream_files_only(self) -> None:
        legacy_path = self.root / "data" / "legacy-unregistered.tsv"
        legacy_path.write_text("id\tvalue\n1\tlegacy\n", encoding="utf-8")

        db_path = self.root / ".research" / "research.sqlite"
        db_path.unlink()
        with closing(sqlite3.connect(db_path)) as connection, connection:
            connection.execute("PRAGMA foreign_keys = ON")
            for migration in sorted(MIGRATION_DIR.rglob("[0-9][0-9][0-9]_*.sql")):
                version = int(migration.name[:3])
                if version > 27:
                    break
                connection.executescript(migration.read_text(encoding="utf-8"))
            connection.execute("PRAGMA user_version = 27")
            connection.execute("DELETE FROM meta WHERE key = 'schema_version'")
            connection.execute(
                "INSERT INTO meta(key, value) VALUES('schema_version', '27')"
            )

        baseline = self._commit("RESEARCH: preserve legacy downstream baseline")

        migrated = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "research_db.py"),
                "--project",
                str(self.root),
                "migrate",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(migrated.returncode, 0, migrated.stdout + migrated.stderr)

        with closing(sqlite3.connect(db_path)) as connection:
            marker = connection.execute(
                "SELECT value FROM meta WHERE key = 'downstream_artifact_legacy_baseline_commit'"
            ).fetchone()
        self.assertIsNotNone(marker)
        self.assertEqual(marker[0], baseline)

        unchanged = validate_completion(self.root)
        orphan_blockers = [
            item
            for item in unchanged["downstream"]["blockers"]
            if item["reason"] == "tracked_downstream_artifacts_unregistered"
        ]
        self.assertFalse(
            any(
                "data/legacy-unregistered.tsv" in item.get("paths", [])
                for item in orphan_blockers
            ),
            orphan_blockers,
        )

        legacy_path.write_text("id\tvalue\n1\tedited-after-migration\n", encoding="utf-8")
        edited = validate_completion(self.root)
        orphan_blockers = [
            item
            for item in edited["downstream"]["blockers"]
            if item["reason"] == "tracked_downstream_artifacts_unregistered"
        ]
        self.assertTrue(
            any(
                "data/legacy-unregistered.tsv" in item.get("paths", [])
                for item in orphan_blockers
            ),
            orphan_blockers,
        )


if __name__ == "__main__":
    unittest.main()

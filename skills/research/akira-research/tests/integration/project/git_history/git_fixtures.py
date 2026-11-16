"""Shared Git + confirmatory Analysis fixture for freeze-history tests.

The research project root can sit at the Git top-level or in a subdirectory, so
the same scenarios cover both layouts.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parents[4] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from research_db_core import init_database  # noqa: E402
from research_db_ops.downstream import record_analysis, record_dataset  # noqa: E402


class GitResearchProject:
    def __init__(self, *, subdirectory: str = "") -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.top = Path(self._tempdir.name).resolve()
        self.root = self.top / subdirectory if subdirectory else self.top
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "RESEARCH.md").write_text("# Research\n\n中文科研状态。\n", encoding="utf-8")
        init_database(self.root)
        self.git("init")
        self.git("config", "user.email", "research@example.test")
        self.git("config", "user.name", "Research Test")
        self.code_path = "../scripts/analyses/trajectory.py" if subdirectory else "scripts/analyses/trajectory.py"

    def cleanup(self) -> None:
        self._tempdir.cleanup()

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(self.top), *args], check=True, text=True, capture_output=True
        ).stdout.strip()

    def commit(self, message: str) -> str:
        self.git("add", "-A")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def write(self, relative: str, text: str) -> Path:
        path = (self.root / relative).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def write_plan_assets(self) -> None:
        self.write("data/sleep/README.md", "# 数据来源\n\n受试者是独立推断单位。\n")
        self.write("data/sleep/raw.csv", "subject,day,y\n1,0,10\n1,1,12\n")
        self.write("analysis/trajectory/README.md", "# 分析计划\n\n主要估计量为每日变化斜率。\n")
        self.write(self.code_path, "print('analysis')\n")

    def record_dataset(self) -> None:
        record_dataset(
            self.root,
            {
                "slug": "sleep-data",
                "title": "Sleep repeated measures",
                "identity": "example:sleep",
                "source": "test fixture",
                "received_at": "2026-08-28T00:00:00+00:00",
                "unit_of_inference": "participant",
                "provenance_path": "data/sleep/README.md",
                "artifacts": [{"role": "raw", "location": "data/sleep/raw.csv"}],
            },
        )

    def analysis_bundle(self, **overrides: Any) -> dict[str, Any]:
        bundle: dict[str, Any] = {
            "slug": "sleep-trajectory",
            "title": "Sleep trajectory analysis",
            "analysis_mode": "confirmatory",
            "status": "planned",
            "target_uncertainty": "Is there a stable positive longitudinal trend?",
            "estimand": "Population-average change per study day",
            "unit_of_inference": "participant",
            "primary_analysis": "Mixed model with participant random intercept and slope",
            "analysis_path": "analysis/trajectory/README.md",
            "code_path": self.code_path,
            "dataset_slugs": ["sleep-data"],
        }
        bundle.update(overrides)
        return bundle

    def freeze_planned_analysis(self) -> str:
        self.write_plan_assets()
        self.record_dataset()
        record_analysis(self.root, self.analysis_bundle())
        return self.commit("ANALYSIS: freeze primary plan")

    def record_result(self, freeze_commit: str) -> str:
        self.write("analysis/trajectory/outputs/primary.csv", "term,estimate\nslope,11.4\n")
        record_analysis(
            self.root,
            self.analysis_bundle(
                status="completed",
                freeze_commit=freeze_commit,
                artifacts=[{"role": "estimate", "path": "analysis/trajectory/outputs/primary.csv"}],
                observations=[
                    {
                        "statement": "A result exists.",
                        "source_path": "analysis/trajectory/outputs/primary.csv",
                    }
                ],
            ),
        )
        return self.commit("ANALYSIS: record primary result")


def blockers_with_reason(result: dict[str, Any], section: str, reason: str) -> list[dict[str, Any]]:
    return [item for item in result[section]["blockers"] if item.get("reason") == reason]

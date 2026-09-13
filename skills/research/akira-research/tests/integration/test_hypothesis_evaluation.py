from __future__ import annotations

import sqlite3
import subprocess
from datetime import datetime, timedelta
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from research_db_core import ResearchDbError, init_database  # noqa: E402
from research_db_ops.completion import validate_completion  # noqa: E402
from research_db_ops.downstream import record_analysis, record_analysis_attempt, record_dataset  # noqa: E402
from research_db_ops.planning import (  # noqa: E402
    record_design,
    record_hypothesis_evaluation,
    record_hypothesis_proposal,
    record_hypothesis_set,
)


class HypothesisEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "hypotheses").mkdir(parents=True)
        (self.root / "designs").mkdir(parents=True)
        (self.root / "data" / "trial-data").mkdir(parents=True)
        (self.root / "analysis" / "primary").mkdir(parents=True)
        (self.root / "scripts" / "analyses").mkdir(parents=True)
        (self.root / "RESEARCH.md").write_text(
            """# Research

## Objective

比较两个随机处理的平均结局差异。

## Applicable Standards

不适用：当前没有额外正式规范。

## Current Loop

QUESTION

## Active Uncertainty

A 相对 B 的平均处理效应属于哪个预定义效应区域？

## Current State

结果前假设、设计、数据与分析溯源按测试步骤逐步登记。

## Active Work

继续取得能够区分预定义效应区域的证据。

## Open Threads

暂无当前优先处理的其他问题。

## Key Decisions

保持结果前冻结与结果后评价分离。

## Navigation

不适用：当前没有其他人类可读科研入口。

## References

- `.research/research.sqlite`
""",
            encoding="utf-8",
        )
        (self.root / "hypotheses" / "treatment-effect.md").write_text(
            """# Hypothesis Set: Treatment effect hypothesis set

## Navigation

- [Research](../RESEARCH.md)

## Target Uncertainty

A 相对 B 的平均处理效应属于哪个预定义效应区域？

## Hypotheses

### H1 — 正向效应

Statement: 平均处理效应位于预定义正向区域。

### H2 — 较小效应

Statement: 平均处理效应低于实际意义阈值。

## Discriminator Matrix

主要估计量及其区间用于区分预定义效应区域。

## Current Evidence

未知：结果尚未可见。

## Decision Boundary

使用结果前定义的效应区域边界。
""",
            encoding="utf-8",
        )
        (self.root / "hypotheses" / "README.md").write_text(
            "# Hypotheses\n\n## Objects\n\n- [Treatment effect hypothesis set](treatment-effect.md) — 冻结的效应区域假设集。\n\n"
            "## Relations\n\n- [Treatment effect hypothesis set](treatment-effect.md) → [Treatment effect design](../designs/treatment-effect.md)\n",
            encoding="utf-8",
        )
        (self.root / "designs" / "treatment-effect.md").write_text(
            """# Design: Treatment effect design

## Navigation

- [Research](../RESEARCH.md)
- [Hypothesis Set](../hypotheses/treatment-effect.md)

## Target Uncertainty

A 相对 B 的平均处理效应属于哪个预定义效应区域？

## Hypotheses and Discriminator

比较预定义效应区域，主要估计量用于判别。

## Estimand / Target Contrast

E[Y(A)-Y(B)]。

## Population / Experimental System

测试总体。

## Sampling and Experimental Unit

个体为独立实验单位。

## Groups / Exposure / Intervention / Comparator

随机分配 A 与 B。

## Measurements and Timepoints

测量个体主要结局。

## Controls and Bias Protection

随机分配保护主要比较。

## Primary Analysis Alignment

按个体估计 A-B 平均差。

## Precision / Sample Size Rationale

测试 fixture 只验证溯源，不声称现实样本量依据。

## Decision Boundary

按结果前效应区域边界判别。

## Exploratory Analyses

不适用：当前没有探索性分析。

## Feasibility / Ethics / Access Constraints

不适用：测试 fixture 无额外限制。

## Freeze and Amendments

该设计在结果可见前冻结。
""",
            encoding="utf-8",
        )
        (self.root / "designs" / "README.md").write_text(
            "# Designs\n\n## Objects\n\n- [Treatment effect design](treatment-effect.md) — 冻结设计。\n\n"
            "## Relations\n\n- [Treatment effect design](treatment-effect.md) → [Treatment effect hypothesis set](../hypotheses/treatment-effect.md), [Primary analysis](../analysis/primary/README.md)\n",
            encoding="utf-8",
        )
        (self.root / "data" / "trial-data" / "README.md").write_text(
            """# Dataset: Trial data

## Navigation

- [Research](../../RESEARCH.md)

## Dataset Identity

测试试验数据集。

## Research Purpose

用于估计 A-B 平均处理效应。

## Source and Version

来源为测试 fixture，当前版本固定。

## Population and Sample Mapping

个体是独立实验单位。

## Data Layers and Artifacts

原始 CSV 为原始数据。

## Metadata / Missingness / Exclusions

不适用：当前没有额外缺失或排除。

## QC and Anomalies

不适用：当前没有会改变分析的异常。

## Processing and Reproduction

分析入口由正式脚本记录。

## Freeze / Access / Ethics

由 Git 提交固定；无额外访问限制。
""", encoding="utf-8"
        )
        (self.root / "data" / "README.md").write_text(
            "# Data\n\n## Objects\n\n- [Trial data](trial-data/README.md) — 测试数据集。\n\n"
            "## Relations\n\n- [Trial data](trial-data/README.md) → [Primary analysis](../analysis/primary/README.md)\n",
            encoding="utf-8",
        )
        (self.root / "data" / "trial-data" / "raw.csv").write_text(
            "subject,treatment,y\n1,A,10\n2,B,9\n", encoding="utf-8"
        )
        (self.root / "analysis" / "primary" / "README.md").write_text(
            """# Analysis: Primary analysis

## Navigation

- [Research](../../RESEARCH.md)
- [研究设计](../../designs/treatment-effect.md)
- [数据集](../../data/trial-data/README.md)

## Question / Target Contrast

估计 A-B 平均处理效应。

## Inputs and Data Freeze

使用 trial-data 冻结输入。

## Unit of Inference

个体。

## Primary Analysis

估计 A-B 平均差及其不确定性。

## Exploratory / Sensitivity Analyses

不适用：当前没有额外探索或敏感性分析。

## Assumptions and Diagnostics

检查主要模型假设与诊断。

## Outputs

结果估计与诊断进入已登记产物。

## Reproduction

入口为 `scripts/analyses/primary.py`。

## Result Boundary

结果仅用于判别预定义效应区域。

## Amendments

不适用：当前没有修订。
""", encoding="utf-8"
        )
        (self.root / "analysis" / "README.md").write_text(
            "# Analyses\n\n## Objects\n\n- [Primary analysis](primary/README.md) — 主要确认性分析。\n\n"
            "## Relations\n\n- [Primary analysis](primary/README.md) → [Treatment effect design](../designs/treatment-effect.md), [Trial data](../data/trial-data/README.md)\n",
            encoding="utf-8",
        )
        (self.root / "scripts" / "analyses" / "primary.py").write_text(
            "print('analysis')\n", encoding="utf-8"
        )
        (self.root / "scripts" / "analyses" / "support.py").write_text(
            "print('support diagnostics')\n", encoding="utf-8"
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

    def _record_planning_and_dataset(self) -> tuple[str, str]:
        scientific_freeze = self._commit("RESEARCH: freeze question and design")
        uncertainty = "A 相对 B 的平均处理效应属于哪个预定义效应区域？"
        estimand = "E[Y(A)-Y(B)]"
        record_hypothesis_proposal(
            self.root,
            {
                "slug": "treatment-effect-regions",
                "origin": "agent",
                "original_statement": "处理效应可能落在预定义的不同效应区域。",
                "rationale": "该 proposal 将当前 Active Uncertainty 操作化为可由预定义边界判别的竞争状态。",
            },
        )
        record_hypothesis_set(
            self.root,
            {
                "slug": "treatment-effect",
                "title": "Treatment effect hypothesis set",
                "target_uncertainty": uncertainty,
                "artifact_path": "hypotheses/treatment-effect.md",
                "status": "frozen",
                "freeze_commit": scientific_freeze,
                "proposal_slugs": ["treatment-effect-regions"],
            },
        )
        record_design(
            self.root,
            {
                "slug": "treatment-effect",
                "title": "Treatment effect design",
                "hypothesis_set_slug": "treatment-effect",
                "target_estimand": estimand,
                "primary_outcome": "individual outcome",
                "experimental_unit": "individual",
                "artifact_path": "designs/treatment-effect.md",
                "status": "frozen",
                "feasibility_status": "ready",
                "freeze_commit": scientific_freeze,
            },
        )
        record_dataset(
            self.root,
            {
                "slug": "trial-data",
                "title": "Trial data",
                "identity": "test:trial:v1",
                "source": "test fixture",
                "received_at": "2026-08-28T00:00:00+00:00",
                "unit_of_inference": "individual",
                "provenance_path": "data/trial-data/README.md",
                "artifacts": [{"role": "raw", "location": "data/trial-data/raw.csv"}],
            },
        )
        return uncertainty, estimand

    def test_hypothesis_freeze_rejects_invalid_human_format_before_state_transition(self) -> None:
        (self.root / "hypotheses" / "treatment-effect.md").write_text(
            "# 假设集合\n\n缺少固定章节和导航。\n",
            encoding="utf-8",
        )
        scientific_freeze = self._commit("RESEARCH: stage invalid hypothesis format")
        record_hypothesis_proposal(
            self.root,
            {
                "slug": "treatment-effect-regions",
                "origin": "agent",
                "original_statement": "处理效应可能落在预定义的不同效应区域。",
                "rationale": "该 proposal 将当前不确定性操作化为竞争状态。",
            },
        )

        with self.assertRaisesRegex(ResearchDbError, "冻结前人类格式检查失败"):
            record_hypothesis_set(
                self.root,
                {
                    "slug": "treatment-effect",
                    "title": "Treatment effect hypothesis set",
                    "target_uncertainty": "A 相对 B 的平均处理效应属于哪个预定义效应区域？",
                    "artifact_path": "hypotheses/treatment-effect.md",
                    "status": "frozen",
                    "freeze_commit": scientific_freeze,
                    "proposal_slugs": ["treatment-effect-regions"],
                },
            )

        with sqlite3.connect(self.root / ".research" / "research.sqlite") as connection:
            row = connection.execute(
                "SELECT status FROM hypothesis_sets WHERE slug='treatment-effect'"
            ).fetchone()
        self.assertIsNone(row)

    def test_design_freeze_rejects_invalid_human_format_before_state_transition(self) -> None:
        scientific_freeze = self._commit("RESEARCH: stage planning artifacts")
        uncertainty = "A 相对 B 的平均处理效应属于哪个预定义效应区域？"
        record_hypothesis_proposal(
            self.root,
            {
                "slug": "treatment-effect-regions",
                "origin": "agent",
                "original_statement": "处理效应可能落在预定义的不同效应区域。",
                "rationale": "该 proposal 将当前不确定性操作化为竞争状态。",
            },
        )
        record_hypothesis_set(
            self.root,
            {
                "slug": "treatment-effect",
                "title": "Treatment effect hypothesis set",
                "target_uncertainty": uncertainty,
                "artifact_path": "hypotheses/treatment-effect.md",
                "status": "frozen",
                "freeze_commit": scientific_freeze,
                "proposal_slugs": ["treatment-effect-regions"],
            },
        )
        (self.root / "designs" / "treatment-effect.md").write_text(
            "# 研究设计\n\n缺少固定章节和上游导航。\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ResearchDbError, "冻结前人类格式检查失败"):
            record_design(
                self.root,
                {
                    "slug": "treatment-effect",
                    "title": "Treatment effect design",
                    "hypothesis_set_slug": "treatment-effect",
                    "target_estimand": "E[Y(A)-Y(B)]",
                    "primary_outcome": "individual outcome",
                    "experimental_unit": "individual",
                    "artifact_path": "designs/treatment-effect.md",
                    "status": "frozen",
                    "feasibility_status": "ready",
                    "freeze_commit": scientific_freeze,
                },
            )

        with sqlite3.connect(self.root / ".research" / "research.sqlite") as connection:
            row = connection.execute(
                "SELECT status FROM research_designs WHERE slug='treatment-effect'"
            ).fetchone()
        self.assertIsNone(row)

    def test_matching_confirmatory_analysis_requires_explicit_design_link(self) -> None:
        uncertainty, estimand = self._record_planning_and_dataset()
        with self.assertRaisesRegex(ResearchDbError, "必须显式提供 design_slug"):
            record_analysis(
                self.root,
                {
                    "slug": "primary",
                    "title": "Primary analysis",
                    "analysis_mode": "confirmatory",
                    "status": "planned",
                    "target_uncertainty": uncertainty,
                    "estimand": estimand,
                    "unit_of_inference": "individual",
                    "primary_analysis": "Welch mean difference",
                    "analysis_path": "analysis/primary/README.md",
                    "code_path": "scripts/analyses/primary.py",
                    "dataset_slugs": ["trial-data"],
                },
            )

    def test_completed_linked_analysis_requires_hypothesis_evaluation(self) -> None:
        uncertainty, estimand = self._record_planning_and_dataset()
        record_analysis(
            self.root,
            {
                "slug": "primary",
                "title": "Primary analysis",
                "analysis_mode": "confirmatory",
                "status": "planned",
                "target_uncertainty": uncertainty,
                "estimand": estimand,
                "unit_of_inference": "individual",
                "primary_analysis": "Welch mean difference",
                "analysis_path": "analysis/primary/README.md",
                "code_path": "scripts/analyses/primary.py",
                "dataset_slugs": ["trial-data"],
                "design_slug": "treatment-effect",
                "artifacts": [
                    {
                        "role": "other",
                        "path": "scripts/analyses/support.py",
                        "timing_role": "pre_result_support",
                    }
                ],
            },
        )
        analysis_freeze = self._commit("ANALYSIS: freeze input and plan")
        record_analysis_attempt(
            self.root,
            {
                "analysis_slug": "primary",
                "attempt_key": "A001",
                "status": "selected",
                "git_commit": analysis_freeze,
                "reason": "Primary prespecified execution.",
                "decision_reason": "This execution implements the frozen primary analysis.",
            },
        )
        result_path = self.root / "analysis" / "primary" / "result.csv"
        result_path.write_text("estimate,low,high\n1,-5,7\n", encoding="utf-8")
        record_analysis(
            self.root,
            {
                "slug": "primary",
                "title": "Primary analysis",
                "analysis_mode": "confirmatory",
                "status": "completed",
                "target_uncertainty": uncertainty,
                "estimand": estimand,
                "unit_of_inference": "individual",
                "primary_analysis": "Welch mean difference",
                "analysis_path": "analysis/primary/README.md",
                "code_path": "scripts/analyses/primary.py",
                "dataset_slugs": ["trial-data"],
                "design_slug": "treatment-effect",
                "freeze_commit": analysis_freeze,
                "artifacts": [
                    {"role": "estimate", "path": "analysis/primary/result.csv"}
                ],
                "observations": [
                    {
                        "statement": "区间仍跨越多个预定义效应区域。",
                        "source_path": "analysis/primary/result.csv",
                    }
                ],
            },
        )
        self._commit("ANALYSIS: record result")

        before = validate_completion(self.root)
        reasons = {item["reason"] for item in before["planning"]["blockers"]}
        self.assertIn("completed_confirmatory_analysis_missing_hypothesis_evaluation", reasons)

        with sqlite3.connect(self.root / ".research" / "research.sqlite") as connection:
            completed_at = connection.execute(
                "SELECT completed_at FROM analysis_runs WHERE slug = 'primary'"
            ).fetchone()[0]
        premature_evaluation = (
            datetime.fromisoformat(completed_at) - timedelta(seconds=1)
        ).isoformat()

        with self.assertRaisesRegex(ResearchDbError, "不能早于.*completed_at"):
            record_hypothesis_evaluation(
                self.root,
                {
                    "hypothesis_set_slug": "treatment-effect",
                    "analysis_slug": "primary",
                    "resolution_status": "unresolved",
                    "decision": "premature evaluation",
                    "summary": "该评价时间早于 Analysis 完成时间，必须拒绝。",
                    "source_path": "analysis/primary/result.csv",
                    "evaluated_at": premature_evaluation,
                },
            )

        record_hypothesis_evaluation(
            self.root,
            {
                "hypothesis_set_slug": "treatment-effect",
                "analysis_slug": "primary",
                "resolution_status": "unresolved",
                "decision": "inconclusive",
                "summary": "主要区间跨越多个预定义效应区域，因此本轮证据不足以区分竞争假设。",
                "source_path": "analysis/primary/result.csv",
            },
        )
        self._commit("INTERPRETATION: record hypothesis evaluation")
        after = validate_completion(self.root)
        self.assertTrue(after["ok"], after["errors"])
        self.assertEqual(after["planning"]["hypothesis_evaluation_count"], 1)

        with self.assertRaisesRegex(ResearchDbError, "不可覆盖"):
            record_hypothesis_evaluation(
                self.root,
                {
                    "hypothesis_set_slug": "treatment-effect",
                    "analysis_slug": "primary",
                    "resolution_status": "resolved",
                    "decision": "changed after seeing result",
                    "summary": "This second evaluation must not overwrite the first event.",
                    "source_path": "analysis/primary/result.csv",
                },
            )

        with sqlite3.connect(self.root / ".research" / "research.sqlite") as connection:
            connection.execute(
                "UPDATE hypothesis_evaluations SET evaluated_at = ? WHERE analysis_id = 1",
                (premature_evaluation,),
            )
        self._commit("TEST: persist invalid evaluation chronology")
        invalid = validate_completion(self.root)
        reasons = {item["reason"] for item in invalid["planning"]["blockers"]}
        self.assertIn("hypothesis_evaluation_before_analysis_completion", reasons)

    def test_dataset_can_append_provenance_artifact_without_changing_identity(self) -> None:
        self._record_planning_and_dataset()
        transform = self.root / "scripts"
        (transform / "curate.py").write_text("print('curate')\n", encoding="utf-8")
        record_dataset(
            self.root,
            {
                "slug": "trial-data",
                "title": "Trial data",
                "identity": "test:trial:v1",
                "source": "test fixture",
                "received_at": "2026-08-28T00:00:00+00:00",
                "unit_of_inference": "individual",
                "provenance_path": "data/trial-data/README.md",
                "artifacts": [{"role": "other", "location": "scripts/curate.py"}],
            },
        )
        result = validate_completion(self.root)
        self.assertIn("scripts/curate.py", set(result["git"]["canonical_paths"]))

        with self.assertRaisesRegex(ResearchDbError, "不能.*静默修改"):
            record_dataset(
                self.root,
                {
                    "slug": "trial-data",
                    "title": "Mutated dataset identity",
                    "identity": "test:trial:v1",
                    "source": "test fixture",
                    "received_at": "2026-08-28T00:00:00+00:00",
                    "unit_of_inference": "individual",
                    "provenance_path": "data/trial-data/README.md",
                    "artifacts": [{"role": "other", "location": "scripts/curate.py"}],
                },
            )


if __name__ == "__main__":
    unittest.main()

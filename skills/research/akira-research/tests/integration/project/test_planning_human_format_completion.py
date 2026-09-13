from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from research_db_core import init_database  # noqa: E402
from research_db_ops.completion import planning_completion_readiness, validate_completion  # noqa: E402
from research_db_ops.planning import (  # noqa: E402
    record_design,
    record_hypothesis_proposal,
    record_hypothesis_set,
)


VALID_RESEARCH_MD = """# Research

## Objective

验证科研规划对象的人类格式与完成门禁。

## Applicable Standards

不适用：当前没有额外正式规范。

## Current Loop

QUESTION

## Active Uncertainty

当前最需要区分的科学解释是什么？

## Current State

当前证据状态已记录。

## Active Work

等待下一条能够区分竞争解释的证据。

## Open Threads

暂无当前优先处理的其他问题。

## Key Decisions

保持当前证据边界。

## Navigation

暂无其他科研入口。

## References

- `.research/research.sqlite`
"""


class PlanningHumanFormatCompletionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "RESEARCH.md").write_text(VALID_RESEARCH_MD, encoding="utf-8")
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

    def test_planning_completion_requires_registered_frozen_artifacts(self) -> None:
        hypotheses = self.root / "hypotheses"
        designs = self.root / "designs"
        hypotheses.mkdir()
        designs.mkdir()
        hypothesis_path = hypotheses / "causal-set.md"
        design_path = designs / "causal-design.md"
        hypothesis_path.write_text(
            """# Hypothesis Set: 因果竞争假设

## Navigation

- [Research](../RESEARCH.md)

## Target Uncertainty

目标因素是否具有独立因果贡献？

## Hypotheses

### H1 — 独立贡献

Statement: 目标因素具有独立因果贡献。

### H2 — 替代解释

Statement: 主要效应由目标因素之外的路径解释。

## Discriminator Matrix

干预对比用于区分两个竞争解释。

## Current Evidence

未知：结果尚未可见。

## Decision Boundary

预定义主要结局差异用于更新假设状态。
""",
            encoding="utf-8",
        )
        design_path.write_text(
            """# Design: 因果判别设计

## Navigation

- [Research](../RESEARCH.md)
- [Hypothesis Set](../hypotheses/causal-set.md)

## Target Uncertainty

目标因素是否具有独立因果贡献？

## Hypotheses and Discriminator

干预对比用于区分竞争解释。

## Estimand / Target Contrast

干预组与对照组的主要结局差异。

## Population / Experimental System

目标实验系统。

## Sampling and Experimental Unit

独立随机化集群。

## Groups / Exposure / Intervention / Comparator

干预组与对照组。

## Measurements and Timepoints

主要结局按预定义时间点测量。

## Controls and Bias Protection

随机化与标准化测量保护主要比较。

## Primary Analysis Alignment

按独立随机化集群估计主要结局差异。

## Precision / Sample Size Rationale

待确认：关键精度参数仍需确认。

## Decision Boundary

按结果前定义的主要对比边界解释。

## Exploratory Analyses

不适用：当前没有探索性分析。

## Feasibility / Ethics / Access Constraints

待确认：关键设施和精度参数仍需确认。

## Freeze and Amendments

进入结果判别前冻结；后续变更必须显式记录。
""",
            encoding="utf-8",
        )
        (hypotheses / "README.md").write_text(
            "# Hypotheses\n\n## Objects\n\n- [因果竞争假设](causal-set.md) — 结果前冻结。\n\n"
            "## Relations\n\n- [因果竞争假设](causal-set.md) → [因果判别设计](../designs/causal-design.md)\n",
            encoding="utf-8",
        )
        (designs / "README.md").write_text(
            "# Designs\n\n## Objects\n\n- [因果判别设计](causal-design.md) — 冻结但存在 feasibility blocker。\n\n"
            "## Relations\n\n- [因果判别设计](causal-design.md) → [因果竞争假设](../hypotheses/causal-set.md)\n",
            encoding="utf-8",
        )

        orphaned = planning_completion_readiness(self.root)
        reasons = {item["reason"] for item in orphaned["blockers"]}
        self.assertIn("hypothesis_artifacts_unregistered", reasons)
        self.assertIn("design_artifacts_unregistered", reasons)

        subprocess.run(
            ["git", "-C", str(self.root), "add", "RESEARCH.md", ".research/research.sqlite", "hypotheses", "designs"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.root), "commit", "-m", "RESEARCH: freeze hypothesis and design"],
            check=True,
            capture_output=True,
        )
        freeze_commit = subprocess.run(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        record_hypothesis_proposal(
            self.root,
            {
                "slug": "causal-direct-effect",
                "origin": "agent",
                "original_statement": "目标因素可能具有独立因果贡献。",
                "rationale": "该解释与当前目标不确定性一致，并需要与替代解释形成可判别预测。",
            },
        )
        record_hypothesis_set(
            self.root,
            {
                "slug": "causal-set",
                "title": "因果竞争假设",
                "target_uncertainty": "目标因素是否具有独立因果贡献？",
                "artifact_path": "hypotheses/causal-set.md",
                "status": "frozen",
                "freeze_commit": freeze_commit,
                "proposal_slugs": ["causal-direct-effect"],
            },
        )
        record_design(
            self.root,
            {
                "slug": "causal-design",
                "title": "因果判别设计",
                "hypothesis_set_slug": "causal-set",
                "target_estimand": "干预组与对照组的主要结局差异",
                "primary_outcome": "主要结局",
                "experimental_unit": "独立随机化集群",
                "artifact_path": "designs/causal-design.md",
                "status": "frozen",
                "feasibility_status": "unresolved",
                "feasibility_summary": "关键设施和精度参数仍需确认。",
                "freeze_commit": freeze_commit,
            },
        )
        ready = planning_completion_readiness(self.root)
        self.assertTrue(ready["ready"], ready["blockers"])
        self.assertEqual(ready["hypothesis_set_count"], 1)
        self.assertEqual(ready["design_count"], 1)
        self.assertEqual(ready["frozen_design_count"], 1)

        subprocess.run(
            ["git", "-C", str(self.root), "add", ".research/research.sqlite"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.root), "commit", "-m", "CHORE: register planning provenance"],
            check=True,
            capture_output=True,
        )
        clean = validate_completion(self.root)
        self.assertTrue(clean["ok"], clean["errors"])
        self.assertIn("hypotheses/causal-set.md", clean["git"]["canonical_paths"])
        self.assertIn("designs/causal-design.md", clean["git"]["canonical_paths"])

        design_path.write_text("# 研究设计\n\n冻结后的设计被未经提交地修改。\n", encoding="utf-8")
        dirty = validate_completion(self.root)
        self.assertFalse(dirty["ok"])
        self.assertTrue(any("designs/causal-design.md" in error for error in dirty["errors"]))



if __name__ == "__main__":
    unittest.main()

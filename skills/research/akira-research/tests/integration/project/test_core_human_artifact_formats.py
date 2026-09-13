from __future__ import annotations

import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from research_db_core import database_path, init_database  # noqa: E402
from research_db_support.schema import latest_version  # noqa: E402
from research_db_ops.completion import validate_completion  # noqa: E402
from research_db_ops.completion.human import core_human_artifact_readiness  # noqa: E402
from research_db_ops.completion.human.legacy import validate_legacy_baseline  # noqa: E402


HYPOTHESIS = """# Hypothesis Set: Main alternatives

## Navigation

- [Research](../RESEARCH.md)

## Target Uncertainty

处理效应属于哪个预定义区域？

## Hypotheses

### H1 — 正向效应

Statement: 处理产生正向效应。

### H2 — 小效应

Statement: 处理效应低于实际意义阈值。

## Discriminator Matrix

| Evidence | H1 | H2 |
| --- | --- | --- |
| 主要估计量 | 高于阈值 | 低于阈值 |

## Current Evidence

未知：结果尚未可见。

## Decision Boundary

主要估计量及其不确定区间用于区分两个区域。
"""

DESIGN = """# Design: Main comparison

## Navigation

- [Research](../RESEARCH.md)
- [Hypothesis Set](../hypotheses/main.md)

## Target Uncertainty

处理效应属于哪个预定义区域？

## Hypotheses and Discriminator

H1 与 H2 由主要估计量及其区间区分。

## Estimand / Target Contrast

处理组减对照组的平均差。

## Population / Experimental System

目标实验总体。

## Sampling and Experimental Unit

独立实验单位为个体。

## Groups / Exposure / Intervention / Comparator

处理组与对照组。

## Measurements and Timepoints

主要结局在预定义时间点测量。

## Controls and Bias Protection

采用随机分配和盲法测量。

## Primary Analysis Alignment

按独立实验单位估计组间平均差。

## Precision / Sample Size Rationale

以能够区分实际意义阈值的估计精度为目标。

## Decision Boundary

使用结果前定义的实际意义阈值。

## Exploratory Analyses

不适用：当前没有探索性分析。

## Feasibility / Ethics / Access Constraints

不适用：当前没有额外可行性限制。

## Freeze and Amendments

当前为草案；进入结果判别前冻结。
"""

STUDY = """# Study: Main execution

## Navigation

- [Research](../../RESEARCH.md)
- [Design](../../designs/main.md)

## Study Identity

主要研究实施记录。

## Source and Experimental Units

独立实验单位为个体。

## Actual Groups / Exposure / Intervention

实际实施处理组与对照组。

## Sample Collection and Processing

样本按预定义流程采集和处理。

## Assays and Measurements

主要结局按预定义测量流程获得。

## Protocol / Materials / Instruments

仪器与材料版本已经记录。

## Batch / Run / Time

批次、运行与时间信息已经记录。

## Failures / Missing Events

不适用：当前没有失败或缺失事件。

## Deviations

不适用：当前没有设计偏离。

## Outputs

原始输出交给对应 Dataset 管理。

## Record Boundary / Corrections

当前记录区分现场事实、解释与后续更正。
"""

DATASET = """# Dataset: Main dataset

## Navigation

- [Research](../../RESEARCH.md)
- [Study](../../study/main/README.md)

## Dataset Identity

主数据集。

## Research Purpose

用于估计主要处理效应。

## Source and Version

来自主研究实施；当前批次已记录。

## Population and Sample Mapping

个体为独立推断单位，样本映射已记录。

## Data Layers and Artifacts

raw 与 derived 数据分层保存。

## Metadata / Missingness / Exclusions

不适用：当前没有额外缺失或排除。

## QC and Anomalies

不适用：当前没有会改变分析的 QC 异常。

## Processing and Reproduction

处理入口由项目脚本记录。

## Freeze / Access / Ethics

当前输入版本与访问边界已记录。
"""

ANALYSIS = """# Analysis: Main analysis

## Navigation

- [Research](../../RESEARCH.md)
- [Design](../../designs/main.md)
- [Dataset](../../data/main/README.md)

## Question / Target Contrast

估计处理组减对照组的平均差。

## Inputs and Data Freeze

使用主数据集的当前冻结输入。

## Unit of Inference

独立个体。

## Primary Analysis

估计组间平均差及其不确定性。

## Exploratory / Sensitivity Analyses

不适用：当前没有额外探索或敏感性分析。

## Assumptions and Diagnostics

主要模型假设与诊断边界已记录。

## Outputs

主要估计量与诊断输出进入登记 artifact。

## Reproduction

入口为 `scripts/analyses/main.py`。

## Result Boundary

结果只支持预定义目标对比，不自动升级因果机制结论。

## Amendments

不适用：当前没有分析修订。
"""

INTERPRETATION = """# Interpretation: Main result

## Navigation

- [Research](../RESEARCH.md)
- [Analysis](../analysis/main/README.md)

## Research Question

处理效应属于哪个预定义区域？

## Current Evidence State

主要估计量已经形成，但解释受设计边界约束。

## Supported

当前数据支持主要组间差异的数值估计。

## Indirectly Supported

不适用：当前没有需要单列的间接支持结论。

## Qualified

因果解释受研究设计范围限制。

## Contradicted

不适用：当前没有明确反证。

## Unresolved

机制解释仍未解决。

## Most Discriminating Next Evidence

需要能够区分剩余机制解释的独立证据。
"""


class CoreHumanArtifactFormatTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "RESEARCH.md").write_text("# Research\n", encoding="utf-8")
        (self.root / "hypotheses").mkdir()
        (self.root / "designs").mkdir()
        (self.root / "study" / "main").mkdir(parents=True)
        (self.root / "data" / "main").mkdir(parents=True)
        (self.root / "analysis" / "main").mkdir(parents=True)
        (self.root / "interpretation").mkdir()
        (self.root / "scripts" / "analyses").mkdir(parents=True)
        (self.root / "hypotheses" / "main.md").write_text(HYPOTHESIS, encoding="utf-8")
        (self.root / "designs" / "main.md").write_text(DESIGN, encoding="utf-8")
        (self.root / "study" / "main" / "README.md").write_text(STUDY, encoding="utf-8")
        (self.root / "data" / "main" / "README.md").write_text(DATASET, encoding="utf-8")
        (self.root / "analysis" / "main" / "README.md").write_text(ANALYSIS, encoding="utf-8")
        (self.root / "interpretation" / "main.md").write_text(INTERPRETATION, encoding="utf-8")
        (self.root / "scripts" / "analyses" / "main.py").write_text("print('ok')\n", encoding="utf-8")
        (self.root / "hypotheses" / "README.md").write_text(
            "# Hypotheses\n\n## Objects\n\n- [Main alternatives](main.md)\n\n"
            "## Relations\n\n- [Main alternatives](main.md) → [Main comparison](../designs/main.md)\n",
            encoding="utf-8",
        )
        (self.root / "designs" / "README.md").write_text(
            "# Designs\n\n## Objects\n\n- [Main comparison](main.md)\n\n"
            "## Relations\n\n- [Main comparison](main.md) → [Main alternatives](../hypotheses/main.md), "
            "[Main execution](../study/main/README.md), [Main analysis](../analysis/main/README.md)\n",
            encoding="utf-8",
        )
        (self.root / "study" / "README.md").write_text(
            "# Studies\n\n## Objects\n\n- [Main execution](main/README.md)\n\n"
            "## Relations\n\n- [Main execution](main/README.md) → [Main comparison](../designs/main.md), "
            "[Main dataset](../data/main/README.md)\n",
            encoding="utf-8",
        )
        (self.root / "data" / "README.md").write_text(
            "# Data\n\n## Objects\n\n- [Main dataset](main/README.md)\n\n"
            "## Relations\n\n- [Main dataset](main/README.md) → [Main execution](../study/main/README.md), "
            "[Main analysis](../analysis/main/README.md)\n",
            encoding="utf-8",
        )
        (self.root / "analysis" / "README.md").write_text(
            "# Analyses\n\n## Objects\n\n- [Main analysis](main/README.md)\n\n"
            "## Relations\n\n- [Main analysis](main/README.md) → [Main comparison](../designs/main.md), "
            "[Main dataset](../data/main/README.md)\n",
            encoding="utf-8",
        )
        (self.root / "interpretation" / "README.md").write_text(
            "# Interpretations\n\n## Objects\n\n- [Main result](main.md)\n\n"
            "## Relations\n\n- [Main result](main.md) → [Main analysis](../analysis/main/README.md)\n",
            encoding="utf-8",
        )
        init_database(self.root)
        now = "2026-09-13T00:00:00+00:00"
        with sqlite3.connect(database_path(self.root)) as connection:
            connection.execute(
                """
                INSERT INTO hypothesis_sets(
                    slug, title, target_uncertainty, artifact_path, status, created_at, updated_at
                ) VALUES ('main', 'Main alternatives', '处理效应属于哪个预定义区域？',
                          'hypotheses/main.md', 'draft', ?, ?)
                """,
                (now, now),
            )
            hypothesis_id = int(connection.execute("SELECT id FROM hypothesis_sets WHERE slug='main'").fetchone()[0])
            connection.execute(
                """
                INSERT INTO research_designs(
                    slug, title, hypothesis_set_id, target_estimand, primary_outcome,
                    experimental_unit, artifact_path, status, feasibility_status,
                    created_at, updated_at
                ) VALUES ('main', 'Main comparison', ?, '处理组减对照组的平均差', '主要结局',
                          '个体', 'designs/main.md', 'draft', 'ready', ?, ?)
                """,
                (hypothesis_id, now, now),
            )
            design_id = int(connection.execute("SELECT id FROM research_designs WHERE slug='main'").fetchone()[0])
            connection.execute(
                """
                INSERT INTO studies(
                    slug, title, design_id, study_type, status, provenance_path,
                    started_at, created_at, updated_at
                ) VALUES ('main', 'Main execution', ?, 'experimental', 'in_progress',
                          'study/main/README.md', ?, ?, ?)
                """,
                (design_id, now, now, now),
            )
            study_id = int(connection.execute("SELECT id FROM studies WHERE slug='main'").fetchone()[0])
            connection.execute(
                """
                INSERT INTO datasets(
                    slug, title, source, received_at, unit_of_inference, provenance_path,
                    status, created_at, updated_at, study_id
                ) VALUES ('main', 'Main dataset', 'main study', ?, '个体',
                          'data/main/README.md', 'active', ?, ?, ?)
                """,
                (now, now, now, study_id),
            )
            dataset_id = int(connection.execute("SELECT id FROM datasets WHERE slug='main'").fetchone()[0])
            connection.execute(
                """
                INSERT INTO analysis_runs(
                    slug, title, analysis_mode, status, target_uncertainty, estimand,
                    unit_of_inference, primary_analysis, analysis_path, code_path,
                    started_at, created_at, updated_at, design_id
                ) VALUES ('main', 'Main analysis', 'exploratory', 'planned',
                          '处理效应属于哪个预定义区域？', '处理组减对照组的平均差', '个体',
                          '估计组间平均差', 'analysis/main/README.md', 'scripts/analyses/main.py',
                          ?, ?, ?, ?)
                """,
                (now, now, now, design_id),
            )
            analysis_id = int(connection.execute("SELECT id FROM analysis_runs WHERE slug='main'").fetchone()[0])
            connection.execute(
                "INSERT INTO analysis_inputs(analysis_id, dataset_id, role) VALUES (?, ?, 'primary')",
                (analysis_id, dataset_id),
            )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_planning_human_artifacts_accept_strict_formats_and_indexes(self) -> None:
        result = core_human_artifact_readiness(self.root)

        self.assertTrue(result["ready"], result["blockers"])
        self.assertEqual(result["artifact_count"], 6)
        self.assertEqual(result["index_count"], 6)

    def test_hypothesis_format_rejects_missing_required_h2(self) -> None:
        path = self.root / "hypotheses" / "main.md"
        path.write_text(
            HYPOTHESIS.replace("## Current Evidence\n\n未知：结果尚未可见。\n\n", "", 1),
            encoding="utf-8",
        )

        result = core_human_artifact_readiness(self.root)

        self.assertFalse(result["ready"])
        self.assertTrue(
            any(
                item["reason"] == "human_markdown_section_order_invalid"
                and item["path"] == "hypotheses/main.md"
                for item in result["blockers"]
            )
        )

    def test_design_navigation_requires_known_hypothesis_upstream(self) -> None:
        path = self.root / "designs" / "main.md"
        path.write_text(
            DESIGN.replace("- [Hypothesis Set](../hypotheses/main.md)\n", "", 1),
            encoding="utf-8",
        )

        result = core_human_artifact_readiness(self.root)

        self.assertFalse(result["ready"])
        blocker = next(
            item for item in result["blockers"]
            if item["reason"] == "human_artifact_upstream_link_missing"
        )
        self.assertEqual(blocker["path"], "designs/main.md")
        self.assertEqual(blocker["target"], "hypotheses/main.md")

    def test_analysis_navigation_requires_known_dataset_and_design(self) -> None:
        path = self.root / "analysis" / "main" / "README.md"
        path.write_text(
            ANALYSIS.replace("- [Dataset](../../data/main/README.md)\n", "", 1),
            encoding="utf-8",
        )

        result = core_human_artifact_readiness(self.root)

        self.assertFalse(result["ready"])
        blocker = next(
            item for item in result["blockers"]
            if item["reason"] == "human_artifact_upstream_link_missing"
            and item["path"] == "analysis/main/README.md"
        )
        self.assertEqual(blocker["target"], "data/main/README.md")

    def test_study_path_is_stable_per_object(self) -> None:
        with sqlite3.connect(database_path(self.root)) as connection:
            connection.execute(
                "UPDATE studies SET provenance_path='study/README.md' WHERE slug='main'"
            )

        result = core_human_artifact_readiness(self.root)

        self.assertFalse(result["ready"])
        blocker = next(
            item for item in result["blockers"]
            if item["reason"] == "human_artifact_path_invalid"
            and item["path"] == "study/README.md"
        )
        self.assertEqual(blocker["expected"], "study/main/README.md")

    def test_interpretation_requires_upstream_human_link_beyond_research_home(self) -> None:
        path = self.root / "interpretation" / "main.md"
        path.write_text(
            INTERPRETATION.replace("- [Analysis](../analysis/main/README.md)\n", "", 1),
            encoding="utf-8",
        )

        result = core_human_artifact_readiness(self.root)

        self.assertFalse(result["ready"])
        self.assertTrue(
            any(
                item["reason"] == "interpretation_upstream_link_missing"
                and item["path"] == "interpretation/main.md"
                for item in result["blockers"]
            )
        )

    def test_public_completion_exposes_human_artifact_gate(self) -> None:
        path = self.root / "data" / "main" / "README.md"
        path.write_text(
            DATASET.replace("## QC and Anomalies\n\n不适用：当前没有会改变分析的 QC 异常。\n\n", "", 1),
            encoding="utf-8",
        )

        result = validate_completion(self.root)

        self.assertIn("human_artifacts", result)
        self.assertFalse(result["human_artifacts"]["ready"])
        self.assertTrue(
            any(
                item["reason"] == "human_markdown_section_order_invalid"
                and item["path"] == "data/main/README.md"
                for item in result["human_artifacts"]["blockers"]
            )
        )

    def test_invalid_human_artifact_legacy_baseline_fails_public_completion(self) -> None:
        with sqlite3.connect(database_path(self.root)) as connection:
            connection.execute(
                "INSERT INTO meta(key, value) VALUES('human_artifact_legacy_baseline_commit', 'deadbeef')"
            )

        result = validate_completion(self.root)

        self.assertFalse(result["human_artifacts"]["ready"])
        self.assertTrue(
            any(
                item["reason"] == "human_artifact_legacy_baseline_invalid"
                for item in result["human_artifacts"]["blockers"]
            )
        )
        self.assertTrue(
            any("人类科研格式迁移基线无效" in error for error in result["errors"]),
            result["errors"],
        )

    def test_human_format_baseline_must_predate_contract_schema_after_future_migration(self) -> None:
        subprocess.run(["git", "init", str(self.root)], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", str(self.root), "config", "user.email", "research@example.test"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.root), "config", "user.name", "Research Test"],
            check=True,
        )
        subprocess.run(["git", "-C", str(self.root), "add", "-A"], check=True)
        subprocess.run(
            ["git", "-C", str(self.root), "commit", "-m", "RESEARCH: current strict format baseline"],
            check=True,
            capture_output=True,
        )
        baseline = subprocess.run(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()

        with patch("research_db_ops.completion.human.legacy.latest_version", return_value=26):
            accepted, blocker = validate_legacy_baseline(
                self.root,
                baseline,
                invalid_reason="human_artifact_legacy_baseline_invalid",
                introduced_in_schema=24,
            )

        self.assertIsNone(accepted)
        self.assertIsNotNone(blocker)
        assert blocker is not None
        self.assertEqual(blocker["reason"], "human_artifact_legacy_baseline_invalid")
        self.assertEqual(blocker["baseline_schema_version"], 25)
        self.assertEqual(blocker["introduced_in_schema"], 24)

    def test_index_must_link_every_registered_object(self) -> None:
        (self.root / "hypotheses" / "README.md").write_text(
            "# Hypotheses\n\n## Objects\n\n不适用：暂无对象。\n\n"
            "## Relations\n\n- [Main alternatives](main.md) → [Main comparison](../designs/main.md)\n",
            encoding="utf-8",
        )

        result = core_human_artifact_readiness(self.root)

        self.assertFalse(result["ready"])
        blocker = next(
            item for item in result["blockers"]
            if item["reason"] == "human_index_missing_object_link"
        )
        self.assertEqual(blocker["path"], "hypotheses/README.md")
        self.assertEqual(blocker["targets"], ["hypotheses/main.md"])

    def test_index_must_expose_known_reverse_relation(self) -> None:
        (self.root / "hypotheses" / "README.md").write_text(
            "# Hypotheses\n\n## Objects\n\n- [Main alternatives](main.md)\n\n"
            "## Relations\n\n不适用：暂无关系。\n",
            encoding="utf-8",
        )

        result = core_human_artifact_readiness(self.root)

        self.assertFalse(result["ready"])
        blocker = next(
            item for item in result["blockers"]
            if item["reason"] == "human_index_missing_relation_link"
        )
        self.assertEqual(blocker["path"], "hypotheses/README.md")
        self.assertEqual(
            blocker["targets"],
            ["designs/main.md", "hypotheses/main.md"],
        )

    def test_unchanged_pre_migration_artifact_is_grandfathered_until_edited(self) -> None:
        subprocess.run(["git", "init", str(self.root)], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", str(self.root), "config", "user.email", "research@example.test"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.root), "config", "user.name", "Research Test"],
            check=True,
        )
        legacy_path = self.root / "hypotheses" / "main.md"
        legacy_path.write_text("# 旧假设记录\n\n这是迁移前已经冻结的人类记录。\n", encoding="utf-8")
        with sqlite3.connect(database_path(self.root)) as connection:
            baseline_version = 23
            connection.execute(f"PRAGMA user_version = {baseline_version}")
            connection.execute(
                "UPDATE meta SET value = ? WHERE key = 'schema_version'",
                (str(baseline_version),),
            )
        subprocess.run(["git", "-C", str(self.root), "add", "-A"], check=True)
        subprocess.run(
            ["git", "-C", str(self.root), "commit", "-m", "RESEARCH: legacy human artifact baseline"],
            check=True,
            capture_output=True,
        )
        baseline_commit = subprocess.run(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
        with sqlite3.connect(database_path(self.root)) as connection:
            connection.execute(f"PRAGMA user_version = {latest_version()}")
            connection.execute(
                "UPDATE meta SET value = ? WHERE key = 'schema_version'",
                (str(latest_version()),),
            )
            connection.execute(
                "INSERT INTO meta(key, value) VALUES('human_artifact_legacy_baseline_commit', ?)",
                (baseline_commit,),
            )

        grandfathered = core_human_artifact_readiness(self.root)

        self.assertTrue(grandfathered["ready"], grandfathered["blockers"])
        self.assertIn("hypotheses/main.md", grandfathered["grandfathered_paths"])

        legacy_path.write_text("# 旧假设记录\n\n迁移后再次修改，但仍未采用新格式。\n", encoding="utf-8")
        edited = core_human_artifact_readiness(self.root)

        self.assertFalse(edited["ready"])
        self.assertNotIn("hypotheses/main.md", edited["grandfathered_paths"])
        self.assertTrue(
            any(
                item["path"] == "hypotheses/main.md"
                and item["reason"] in {"human_markdown_h1_invalid", "human_markdown_section_order_invalid"}
                for item in edited["blockers"]
            )
        )


if __name__ == "__main__":
    unittest.main()

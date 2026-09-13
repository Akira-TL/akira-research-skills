from __future__ import annotations

RESEARCH_MD = """# Research

## Objective

判断真实环境与当地牦牛粪便之间是否存在可重复的生态对应关系，并区分牦牛特异模式与一般反刍动物规律。

## Applicable Standards

不适用：当前示例项目没有额外正式报告规范。

## Current Loop

COMMUNICATION

## Active Uncertainty

牦牛与当地环境的对应关系是否强于其他反刍动物，并足以支持后续机制研究？

## Current State

多个基础替代解释已被排除或限定，当前证据链已经进入正式分析、解释与论文传播阶段。

## Active Work

维护可点击的人类科研链，并从中立稿件生成可重放的目标期刊版本。

## Open Threads

机制层面的因果解释仍待独立证据检验。

## Key Decisions

研究树中的并列关系只由显式父子关系和科研关系决定；论文内容只维护一份规范可编辑来源。

## Navigation

- [研究树](research-tree/README.md)
- [假设](hypotheses/README.md)
- [研究设计](designs/README.md)
- [研究实施](study/README.md)
- [数据](data/README.md)
- [分析](analysis/README.md)
- [解释](interpretation/README.md)
- [论文稿件](communication/yak-ecology/manuscript.md)

## References

- `.research/research.sqlite`
"""

HYPOTHESIS = """# Hypothesis Set: Matched correspondence alternatives

## Navigation

- [Research](../RESEARCH.md)

## Target Uncertainty

牦牛与当地环境的对应关系是否强于其他反刍动物？

## Hypotheses

### H1 — 牦牛优势

Statement: 牦牛的当地环境对应关系强于对照反刍动物。

### H2 — 一般反刍动物规律

Statement: 当地环境对应关系存在，但牦牛不表现出额外优势。

## Discriminator Matrix

| Evidence | H1 | H2 |
| --- | --- | --- |
| 匹配比较 | 牦牛优势为正 | 物种间无额外优势 |

## Current Evidence

当前证据支持进入预定义比较，但机制解释仍未解决。

## Decision Boundary

主要物种间 contrast 及其不确定区间用于区分两个解释。
"""

DESIGN = """# Design: Matched comparison

## Navigation

- [Research](../RESEARCH.md)
- [Hypothesis Set](../hypotheses/main.md)

## Target Uncertainty

牦牛的匹配生态对应关系是否强于其他反刍动物？

## Hypotheses and Discriminator

H1 与 H2 由预定义物种间匹配对比量区分。

## Estimand / Target Contrast

牦牛 匹配生态对应关系 减去对照反刍动物 匹配生态对应关系。

## Population / Experimental System

来自相同地理单元的环境与反刍动物配对样本。

## Sampling and Experimental Unit

独立地理配对单元作为主要推断单位。

## Groups / Exposure / Intervention / Comparator

牦牛与 cattle/sheep 作为预定义比较组。

## Measurements and Timepoints

使用同一采样窗口内的环境与粪便群落测量。

## Controls and Bias Protection

匹配地理单元、统一测量流程并预定义主要 contrast。

## Primary Analysis Alignment

主要分析直接估计预定义物种间 匹配对比量。

## Precision / Sample Size Rationale

当前黑盒固定样例只验证 追溯记录 与流程，不宣称现实研究样本量充分。

## Decision Boundary

主要 contrast 的方向与不确定区间共同限定结论。

## Exploratory Analyses

机制候选只作为后续问题，不进入主要结论。

## Feasibility / Ethics / Access Constraints

当前固定样例没有额外访问或伦理限制。

## Freeze and Amendments

主要 contrast 在结果解释前固定；后续修改必须作为显式新版本处理。
"""

STUDY = """# Study: Matched field execution

## Navigation

- [Research](../../RESEARCH.md)
- [Design](../../designs/main.md)

## Study Identity

当地环境与反刍动物配对采样的实施记录。

## Source and Experimental Units

独立地理配对单元为主要实验/观察单位。

## Actual Groups / Exposure / Intervention

实际包含牦牛与对照反刍动物配对样本。

## Sample Collection and Processing

环境与粪便样本按统一流程收集和处理。

## Assays and Measurements

群落测量使用同一分析平台与预定义输出。

## Protocol / Materials / Instruments

协议、材料和仪器身份均由项目记录固定。

## Batch / Run / Time

批次、运行与采样时间均有对应记录。

## Failures / Missing Events

不适用：固定黑盒样例没有额外失败事件。

## Deviations

不适用：固定黑盒样例没有设计偏离。

## Outputs

原始与整理后数据进入主 数据集。

## Record Boundary / Corrections

事实记录、解释和后续更正保持可区分。
"""

DATASET = """# Dataset: Matched ecology dataset

## Navigation

- [Research](../../RESEARCH.md)
- [Study](../../study/main/README.md)

## Dataset Identity

当地环境与反刍动物 matched comparison 主数据集。

## Research Purpose

用于估计预定义物种间 匹配生态对应关系 contrast。

## Source and Version

来自主研究实施；外部来源版本不适用。

## Population and Sample Mapping

地理配对单元与物种样本映射已经记录。

## Data Layers and Artifacts

原始数据与派生数据 层分开保存并可重放。

## Metadata / Missingness / Exclusions

固定样例没有额外缺失或排除。

## QC and Anomalies

固定样例没有会改变主要结论的 QC 异常。

## Processing and Reproduction

处理入口由项目脚本与分析追溯记录固定。

## Freeze / Access / Ethics

当前输入状态、访问边界和使用范围已经记录。
"""

ANALYSIS = """# Analysis: Matched advantage analysis

## Navigation

- [Research](../../RESEARCH.md)
- [Design](../../designs/main.md)
- [数据集](../../data/main/README.md)

## Question / Target Contrast

牦牛 匹配生态对应关系 减去对照反刍动物 匹配生态对应关系。

## Inputs and Data Freeze

使用主 数据集 的固定输入状态。

## Unit of Inference

独立地理配对单元。

## Primary Analysis

估计预定义物种间 contrast 及其不确定性。

## Exploratory / Sensitivity Analyses

机制候选只作为后续探索，不替代主要 contrast。

## Assumptions and Diagnostics

主要估计所依赖的独立性与测量一致性边界已经记录。

## Outputs

主要估计结果与诊断输出均由项目 追溯记录 管理。

## Reproduction

入口为 `scripts/analyses/main.py`。

## Result Boundary

结果支持 matched advantage 的估计，不自动升级为因果机制结论。

## Amendments

不适用：固定黑盒样例没有分析修订。
"""

INTERPRETATION = """# Interpretation: Matched ecology result

## Navigation

- [Research](../RESEARCH.md)
- [Analysis](../analysis/main/README.md)

## Research Question

牦牛的 matched ecological correspondence 是否强于其他反刍动物？

## Current Evidence State

基础替代解释已被否定或限定，主要 匹配对比量 支持继续讨论牦牛候选特征。

## Supported

当前分析支持存在可解释的 匹配生态对应关系 差异。

## Indirectly Supported

后续机制研究具有合理优先级，但尚未得到直接机制证据。

## Qualified

结论仅限当前采样与测量边界，不外推为普遍因果机制。

## Contradicted

“牦牛仅仅因为环境相关菌更多而表现差异”等基础解释不被当前证据支持。

## Unresolved

造成物种间差异的具体机制仍未解决。

## Most Discriminating Next Evidence

需要独立数据区分宿主选择、环境暴露与生态过滤等机制解释。
"""

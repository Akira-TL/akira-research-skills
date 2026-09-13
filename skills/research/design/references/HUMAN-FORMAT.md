# Research Design 人类格式

本文件是 Research Design 长期人类 Markdown 的唯一格式 authority。公共人类文件规则见 `akira-research/references/human/CONTRACT.md`；identification、measurement、bias、precision 与 feasibility 等科学语义仍由 [`CONTRACT.md`](CONTRACT.md) 定义。

## 固定路径与索引

单个 Design 固定为 `designs/<slug>.md`；目录索引固定为 `designs/README.md`。一级标题必须且只能为：

```text
# Design: <title>
```

二级章节必须使用下面模板中的完整集合与顺序。某项对当前研究不适用时写明“不适用”，不能删除标题。首次从 draft 进入 frozen / execution-ready 前，`research-db` 会对固定路径、H1/H2、链接完整性和已知上游 Navigation 做机械 preflight；未通过时不得记录 freeze。Design 冻结后不为了后来出现的 Study、Dataset 或 Analysis 回写正文链接；反向发现由目录索引与 Research Tree 承担。

## 完整模板

```markdown
# Design: <title>

## Navigation

- [Research](../RESEARCH.md)
- [Hypothesis Set](../hypotheses/<slug>.md)

## Target Uncertainty

<当前 Research Question / Active Uncertainty。>

## Hypotheses and Discriminator

<相关 Hypothesis、prediction 与 discriminator；描述性研究可写不适用及原因。>

## Estimand / Target Contrast

<population/system、condition/exposure/intervention、comparator、outcome、time 与 estimand。>

## Population / Experimental System

<目标总体、系统和 scope。>

## Sampling and Experimental Unit

<sampling frame、实验/观察单位、独立推断单位。>

## Groups / Exposure / Intervention / Comparator

<实际计划的组别、暴露、干预与 comparator。>

## Measurements and Timepoints

<measurement、assay、timepoint 与 validity 边界。>

## Controls and Bias Protection

<randomization、blinding、control、confounding / selection / batch protection。>

## Primary Analysis Alignment

<Design 如何支持预定义主要分析和 unit of inference。>

## Precision / Sample Size Rationale

<精度、样本量或信息量依据；未知真实参数不得伪造。>

## Decision Boundary

<结果前停止/判别/实际意义边界。>

## Exploratory Analyses

不适用：当前没有结果前预定义的探索性分析。

## Feasibility / Ethics / Access Constraints

<现实执行、伦理、样本、权限或资源边界。>

## Freeze and Amendments

<当前 freeze 状态；结果前/结果后 amendment 的边界。>
```

## 章节职责与扩展

`Navigation` 至少链接 `RESEARCH.md`；存在关联 Hypothesis Set 时必须链接其 canonical 人类 artifact。Question-driven Design 没有 Hypothesis 时不要制造假设链接。其余 H2 分别固定科学目标、识别、执行与结果前边界。具体 sampling strata、assay panel、power calculation、protocol 参数或伦理细节使用 H3+ 展开。

格式严格不等于科学上强制每个设计使用同一种方法。不同领域可以在 H3+ 使用各自规范，但不能通过删掉 H2 隐藏“当前不适用、未知或尚待确认”的状态。

## 缺失状态

必需 H2 不得留空。统一使用 `不适用：<原因>`、`未记录：<原因>`、`未知：<内容>` 或 `待确认：<事实>`。真实 feasibility blocker 写入相应章节，不用假设值把设计伪装成 execution-ready。

## 目录索引

`designs/README.md` 固定为：

```markdown
# Designs

## Objects

- [<title>](<slug>.md) — <draft/frozen/execution-ready 与最短用途说明>

## Relations

- [<Design>](<slug>.md) → [<Hypothesis Set>](../hypotheses/<hypothesis-slug>.md), [<Study>](../study/<study-slug>/README.md), [<Analysis>](../analysis/<analysis-slug>/README.md)
```

`Objects` 必须覆盖全部已登记 Design。`Relations` 保存当前数据库已知的上游 Hypothesis 与下游 Study / Analysis；Question-driven Design 没有某类关系时不制造链接，全部关系均不存在时显式写 `不适用：当前没有已登记的相关人类科研对象。`。下游对象产生后更新该索引作为反向入口；冻结 Design 本身不回写。

## 合格示例

Question-driven observational Design 可以在 `Hypotheses and Discriminator` 写“不适用：当前目标是估计描述性参数，不存在结果前 competing Hypothesis”，同时完整保留 estimand、sampling、measurement、bias protection 与 precision 章节。

## 代表性错误

删除“不适用”的章节；把实际 Study deviation 回写成“原计划如此”；Design 已冻结后新增下游 Analysis 链接；使用 `design-final.md` 保存所谓最终版；Navigation 指向 `.research/`；目录索引漏掉已登记 Design。

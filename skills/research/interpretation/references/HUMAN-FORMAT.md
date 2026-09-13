# Interpretation 人类格式

本文件是项目级 Interpretation 长期人类 Markdown 的唯一格式 authority。公共人类文件规则见 `akira-research/references/human/CONTRACT.md`；Observation → Claim、证据强度、因果/机制边界与 contradiction 处理仍由 [`CONTRACT.md`](CONTRACT.md) 和 [`EVIDENCE-SYNTHESIS.md`](EVIDENCE-SYNTHESIS.md) 定义。

## 固定路径与索引

单个 Interpretation 固定为 `interpretation/<slug>.md`；目录索引固定为 `interpretation/README.md`。不建立嵌套 `interpretation/<slug>/README.md`，避免与 Analysis / Dataset 的目录语义混淆。一级标题必须且只能为：

```text
# Interpretation: <title>
```

二级章节必须使用下面模板中的完整集合与顺序。

## 完整模板

```markdown
# Interpretation: <title>

## Navigation

- [Research](../RESEARCH.md)
- [Analysis](../analysis/<slug>/README.md)

## Research Question

<本次解释回答的 Research Question / Active Uncertainty。>

## Current Evidence State

<当前 Observation、Design/Study/Analysis 与 Literature 边界的最短综合。>

## Supported

<当前直接证据支持的最窄 Claim、scope 与 evidence pointer。>

## Indirectly Supported

不适用：当前没有仅由间接证据支持的额外 Claim。

## Qualified

<限制、边界条件、替代解释或使 Claim 需要收窄的 evidence。>

## Contradicted

不适用：当前没有需要单列的可信反证。

## Unresolved

<当前证据仍不能区分的问题、解释或 inference gap。>

## Most Discriminating Next Evidence

<最可能降低当前主要不确定性的下一条 observation / experiment / analysis。>
```

## 章节职责与扩展

`Navigation` 至少链接项目 `RESEARCH.md`，并至少链接一个真实上游人类科研 artifact，通常是产生本次 Observation 的 Analysis；还可以链接相关 Design、Study、Dataset、Hypothesis 或 Literature synthesis。人类导航只指向 canonical 人类入口，不把 `.research/` 机器记录作为正常阅读入口。

`Research Question` 固定解释目标；`Current Evidence State` 总结证据边界；`Supported`、`Indirectly Supported`、`Qualified`、`Contradicted`、`Unresolved` 分开不同证据状态，不能把它们合并成自由叙事后隐藏反证或 inference gap；`Most Discriminating Next Evidence` 把剩余不确定性送回 Research Tree。

具体 Claim、Observation、evidence family、scope、alternative explanation 可以在相应 H2 下使用 H3+ 展开。H3+ 数量不受限制；不得新增自由 H2 改变固定信息结构。

## 缺失状态

必需 H2 不得留空。没有某类证据时写 `不适用：<原因>`；资料没有记录写 `未记录：<原因>`；当前无法判断写 `未知：<内容>`；等待必要确认写 `待确认：<事实>`。`Unresolved` 不能因为希望形成完整故事而被省略；若当前确实没有会改变主要答案的剩余不确定性，也要明确写出其 scope。

## 目录索引

`interpretation/README.md` 固定为：

```markdown
# Interpretations

## Objects

- [<title>](<slug>.md) — <最短结论范围与状态说明>

## Relations

- [<Interpretation>](<slug>.md) → [<Analysis>](../analysis/<analysis-slug>/README.md)
```

`Objects` 覆盖 `interpretation/` 下全部正式 Interpretation。`Relations` 至少复现每个 Interpretation 正文中 Research 首页之外的真实上游人类入口；当前没有合法上游关系时 Interpretation 本身不能通过 completion。该索引还承担后续 Communication、新 Research Question 或其他下游工作的反向发现；不为了新增下游对象回写结果前已经冻结的 Hypothesis / Design。

## 合格示例

一个 Analysis 得到稳定效应估计，但机制证据不足时，`Supported` 只写目标 contrast，`Qualified` 写 measurement / external-validity 边界，`Unresolved` 保留机制替代解释，`Most Discriminating Next Evidence` 指向真正能区分这些解释的新实验或分析。不能因为结果统计显著就把机制写进 `Supported`。

## 代表性错误

以下均不合格：把所有证据状态合并成一个“Discussion” H2；删除没有反证的 `Contradicted`；只链接 `.research` 中的结果文件而没有人类上游入口；把作者 Claim 当作独立 evidence；隐藏与首选叙事冲突的 Observation；创建嵌套 `interpretation/<slug>/README.md`；目录索引遗漏正式 Interpretation。

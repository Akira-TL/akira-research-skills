# Analysis 人类格式

本文件是 Analysis 长期人类 Markdown 的唯一格式 authority。公共人类文件规则见 `akira-research/references/human/CONTRACT.md`；统计目标、结果前冻结、诊断、敏感性分析与结果边界仍由 [`RESEARCH-CONTRACT.md`](RESEARCH-CONTRACT.md) 定义。

## 固定路径与索引

每个 Analysis 固定使用 `analysis/<slug>/README.md`；目录索引固定为 `analysis/README.md`。一级标题必须且只能为：

```text
# Analysis: <title>
```

二级章节必须使用下面模板中的完整集合与顺序。Analysis 的代码与机器运行目录不放在该 README 结构中；代码继续使用 `scripts/analyses/`、`src/` 等正式执行入口，Attempt 继续使用 `.research/analysis/` 机器区。

## 完整模板

```markdown
# Analysis: <title>

## Navigation

- [Research](../../RESEARCH.md)
- [Design](../../designs/<slug>.md)
- [Dataset](../../data/<slug>/README.md)

## Question / Target Contrast

<当前 Research Question、estimand 或 exploratory objective。>

## Inputs and Data Freeze

<输入 Dataset、版本/freeze 与会影响解释的输入边界。>

## Unit of Inference

<真实独立推断单位及 pairing / clustering / repeated-measures 结构。>

## Primary Analysis

<主要模型、contrast、multiplicity 与 effect / uncertainty 输出。>

## Exploratory / Sensitivity Analyses

不适用：当前没有额外探索或敏感性分析。

## Assumptions and Diagnostics

<会改变结论的主要假设、诊断和 failure mode。>

## Outputs

<主要 estimate、diagnostic、table、figure 或其他已登记结果 artifact。>

## Reproduction

<正式代码/命令入口、配置与重建边界。>

## Result Boundary

<结果直接显示什么、没有识别什么，以及不能升级到哪些更强 Claim。>

## Amendments

不适用：当前没有结果前或结果后修订。
```

## 章节职责与扩展

`Navigation` 至少链接 `RESEARCH.md`；存在结构化关联 Design 时必须链接该 Design；每个已登记输入 Dataset 都必须链接其 canonical 人类 README。Study 等其他已知上游对象可以继续加入，但不把 `.research/` 机器目录做成人类入口。

`Question / Target Contrast` 固定本 Analysis 真正回答的问题；`Inputs and Data Freeze` 与 `Unit of Inference` 固定输入和统计单位；`Primary Analysis`、`Assumptions and Diagnostics`、`Exploratory / Sensitivity Analyses` 记录分析语义；`Outputs` 与 `Reproduction` 让结果可以定位和重建；`Result Boundary` 负责限制解释范围；`Amendments` 保留结果前/结果后变更时序。

模型规格、多个 sensitivity、diagnostic、subgroup 或 figure 可以在对应 H2 下用 H3+ 展开；不得增加新的 H2 代替固定槽位，也不机械限制分析数量、图数量或字数。

## 缺失状态

必需 H2 不得留空。真实不适用写 `不适用：<原因>`；历史信息没有记录写 `未记录：<原因>`；事实不明写 `未知：<内容>`；等待外部事实或人工确认写 `待确认：<事实>`。不能以默认参数或推测值填补科学输入。

## 目录索引

`analysis/README.md` 固定为：

```markdown
# Analyses

## Objects

- [<title>](<slug>/README.md) — <planned/frozen/completed/abandoned 与最短目标说明>

## Relations

- [<Analysis>](<slug>/README.md) → [<Design>](../designs/<design-slug>.md), [<Dataset>](../data/<dataset-slug>/README.md)
```

`Objects` 必须覆盖全部已登记 Analysis。`Relations` 保存当前数据库已知的关联 Design 与全部输入 Dataset；当前没有已登记关系时显式写 `不适用：当前没有已登记的相关人类科研对象。`。索引还可以在 Interpretation 或 Communication 出现后继续增加可核验反向发现信息；结果前已冻结的上游 Design / Hypothesis 不因此回写。

## 合格示例

一个确认性 Analysis 在 `Navigation` 同时链接冻结 Design 和两个输入 Dataset，在 `Primary Analysis` 明确目标 contrast，在 `Assumptions and Diagnostics` 写主要模型诊断，在 `Result Boundary` 说明当前结果只能回答预定义 estimand。若后来新增结果后 sensitivity，在 `Exploratory / Sensitivity Analyses` 和 `Amendments` 中明确 post-result 时序，而不是改写原 primary plan。

## 代表性错误

以下均不合格：把 `analysis/<slug>/README.md` 改成自由散文；遗漏已登记输入 Dataset 的导航；把 `.research/analysis/<slug>/<attempt>/` 当普通人类入口；删除无 amendment 的 `Amendments`；用“显著”替代 effect / uncertainty；结果后修改 primary plan 却不记录 amendment；目录索引遗漏已登记 Analysis。

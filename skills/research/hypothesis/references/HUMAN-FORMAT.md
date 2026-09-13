# Hypothesis Set 人类格式

本文件是 Hypothesis Set 长期人类 Markdown 的唯一格式 authority。公共人类文件规则见 `akira-research/references/human/CONTRACT.md`；科学语义仍由 [`CONTRACT.md`](CONTRACT.md) 定义。

## 固定路径与索引

单个对象固定为 `hypotheses/<slug>.md`；目录索引固定为 `hypotheses/README.md`。同一 Hypothesis Set 不建立 `v2`、`final` 等副本。冻结后不为了后来出现的 Design、Analysis 或 Claim 回写下游链接；反向发现由目录索引和 Research Tree 承担。

一级标题必须且只能为：

```text
# Hypothesis Set: <title>
```

二级章节必须严格使用下面模板中的集合与顺序。Hypothesis 数量是科学内容，不固定；每个 Hypothesis 使用 H3 及更深层级展开。首次从 draft 进入 frozen 前，`research-db` 会对固定路径、H1/H2、链接完整性和已知上游 Navigation 做机械 preflight；未通过时不得记录 freeze。

## 完整模板

```markdown
# Hypothesis Set: <title>

## Navigation

- [Research](../RESEARCH.md)

## Target Uncertainty

<当前需要区分的 Research Question / Active Uncertainty。>

## Hypotheses

### H1 — <short name>

Statement: <可证伪陈述>

Scope: <适用范围>

Key assumptions:
- <assumption>

Predictions:
- <observable prediction>

Falsifiers:
- <会实质削弱该假设的 observation>

### H2 — <short name>

<同样结构；按真实竞争解释继续增加 H3。>

## Discriminator Matrix

<比较各 Hypothesis 对同一可观测 evidence 的不同 prediction。>

## Current Evidence

未知：结果尚未可见。

## Decision Boundary

<结果前定义哪些 observation 会 favor / weaken / qualify 哪些假设。>
```

## 章节职责与扩展

`Navigation` 只链接创建时已经存在的人类科研入口，至少链接项目 `RESEARCH.md`；已知上游对象可以继续加入。`Target Uncertainty` 固定科学问题。`Hypotheses` 保存 competing explanations；变量数量只在 H3+ 展开。`Discriminator Matrix` 保存真正区分假设的 prediction。`Current Evidence` 只记录当前已有证据状态，不能把“证据不足”写成新的 competing explanation。`Decision Boundary` 保存结果前判别规则。

H3+ 可自由增加 scope、assumption、prediction、falsifier、领域注释和判别细节；不得增加新的 H2 绕过固定结构。

## 缺失状态

必需 H2 不得留空。使用 `不适用：<原因>`、`未记录：<原因>`、`未知：<内容>` 或 `待确认：<事实>`。冻结前应把真正可恢复的信息补全；无法恢复的历史事实必须写“未记录”，不能猜测。

## 目录索引

`hypotheses/README.md` 固定为：

```markdown
# Hypotheses

## Objects

- [<title>](<slug>.md) — <最短必要状态/用途说明>

## Relations

- [<Hypothesis Set>](<slug>.md) → [<Design>](../designs/<design-slug>.md)
```

`Objects` 必须覆盖当前已登记的全部 Hypothesis Set。`Relations` 保存当前数据库已知的人类科研对象关系；存在下游 Design 时至少同时链接该 Hypothesis Set 与 Design。当前没有已登记关系时显式写 `不适用：当前没有已登记的相关人类科研对象。`。可更新索引承担反向发现；不能因此修改已冻结正文。

## 合格示例

两个竞争解释可以都放在 `## Hypotheses` 下作为 `### H1`、`### H2`，并共同指向一个 Discriminator Matrix。后续 Design 出现后，Hypothesis 已冻结时只更新 `hypotheses/README.md` 或 Research Tree，不给冻结文件补“下游 Design”章节。

## 代表性错误

以下均不合格：把每个 Hypothesis 写成新的 H2；删除 `Current Evidence`；使用 `# Hypothesis v2`；在 `Navigation` 写本机绝对路径或 `.research/` 链接；结果可见后回写 frozen Hypothesis 的 prediction；目录索引遗漏已登记对象。

# Dataset 人类格式

本文件是 Dataset 长期人类 Markdown 的唯一格式 authority。公共人类文件规则见 `akira-research/references/human/CONTRACT.md`；Dataset identity、QC、transformation、freeze 与 external storage 的科学/溯源语义继续由 [`CONTRACT.md`](CONTRACT.md) 定义。

## 固定路径与索引

每个 Dataset 固定使用 `data/<slug>/README.md`；目录索引固定为 `data/README.md`。一级标题必须且只能为：

```text
# Dataset: <title>
```

二级章节必须使用下面模板中的完整集合与顺序。

## 完整模板

```markdown
# Dataset: <title>

## Navigation

- [Research](../../RESEARCH.md)
- [Study](../../study/<slug>/README.md)

## Dataset Identity

<稳定 identity、status 与用途范围。>

## Research Purpose

<该 Dataset 为什么进入当前 Research Question / Analysis。>

## Source and Version

<来源、版本、accession / received / collected 时间及 source URL/pointer。>

## Population and Sample Mapping

<population/system、Sample / participant / experimental unit 映射与 unit of inference。>

## Data Layers and Artifacts

<raw、curated、derived、metadata、manifest 等层级与主要 artifact。>

## Metadata / Missingness / Exclusions

<关键 metadata、missingness、exclusion 及其 timing。>

## QC and Anomalies

<QC 诊断、异常、failure mode 与处理边界。>

## Processing and Reproduction

<从 raw 到当前层级的代码/workflow/命令入口与关键 transformation。>

## Freeze / Access / Ethics

<analysis-ready snapshot / freeze、访问控制、伦理与外部存储边界。>
```

## 章节职责与扩展

`Navigation` 至少链接 `RESEARCH.md`；Dataset 来自本项目 Study 时必须链接该 Study 的 canonical 人类记录。外部公开/合作 Dataset 没有本项目 Study 时不制造 Study 链接，并在 `Source and Version` 明确真实来源。变量字典、Sample mapping、QC 指标、数据层级和 transformation 可以在相应 H2 下使用 H3+ 展开。

文件存在不等于科学证据。人类 README 解释 Dataset 身份与边界，机器级大量 artifact 仍可由数据库和 manifest 追踪。

## 缺失状态

必需 H2 不得为空。无法恢复的 metadata 写 `未记录`；科学事实不明写 `未知`；等待合作方或权限确认写 `待确认`；某类信息确实不适用写 `不适用`。不得用默认值或推测补齐。

## 目录索引

`data/README.md` 固定为：

```markdown
# Data

## Objects

- [<title>](<slug>/README.md) — <来源、状态与最短用途说明>

## Relations

- [<Dataset>](<slug>/README.md) → [<Study>](../study/<study-slug>/README.md), [<Analysis>](../analysis/<analysis-slug>/README.md)
```

`Objects` 必须覆盖全部已登记 Dataset。`Relations` 保存当前数据库已知的来源 Study 与消费该 Dataset 的 Analysis；当前没有已登记关系时显式写 `不适用：当前没有已登记的相关人类科研对象。`。后续 Analysis 的反向入口通过该索引或 Research Tree 更新，不要求回写已经冻结的上游科研对象。

## 合格示例

外部公开 Dataset 可以在 `Navigation` 只链接 `RESEARCH.md`，在 `Source and Version` 写 accession、release/version 与获取日期，并在 `Freeze / Access / Ethics` 明确公开访问条件。来自本项目 Study 的 Dataset 则额外链接对应 Study。

## 代表性错误

使用 `data/sleep/README.md` 登记 slug=`sleep-data`；把 raw 原地覆盖后仍称其为原始数据；删除“无异常”的 QC 章节；把 `.research/` 机器路径做成普通人类导航；目录索引漏掉已登记 Dataset。

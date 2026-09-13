# Study 人类格式

本文件是 Study 实际实施记录长期人类 Markdown 的唯一格式 authority。公共人类文件规则见 `akira-research/references/human/CONTRACT.md`；现场事实、同时期解释、追溯解释与更正的证据纪律继续由 [`EXPERIMENT-LOG.md`](EXPERIMENT-LOG.md) 定义。

## 固定路径与索引

每个 Study 固定使用 `study/<slug>/README.md`；目录索引固定为 `study/README.md`。一级标题必须且只能为：

```text
# Study: <title>
```

二级章节严格使用下列模板中的完整集合与顺序。Study 记录的是“实际发生了什么”，不能用它改写 frozen Design。

## 完整模板

```markdown
# Study: <title>

## Navigation

- [Research](../../RESEARCH.md)
- [Design](../../designs/<slug>.md)

## Study Identity

<Study identity、study type、执行状态和关键时间边界。>

## Source and Experimental Units

<participant/source、experimental unit 与稳定 identity。>

## Actual Groups / Exposure / Intervention

<实际发生的组别、暴露或干预；与计划不一致时如实记录。>

## Sample Collection and Processing

<实际采样、处理、aliquot / specimen 流程与身份映射。>

## Assays and Measurements

<实际 Assay / measurement、Sample-to-Assay 映射及状态。>

## Protocol / Materials / Instruments

<protocol、材料版本、仪器、软件与 operator；仅记录会影响解释或复现者。>

## Batch / Run / Time

<batch、plate、lane、run、时间等实施维度。>

## Failures / Missing Events

不适用：当前没有失败或缺失事件。

## Deviations

不适用：当前没有相对 Design 的实施偏离。

## Outputs

<raw output、manifest、execution log 等位置及向 Dataset 的交接。>

## Record Boundary / Corrections

<直接记录、同时期解释、追溯解释/更正的边界与 source pointer。>
```

## 章节职责与扩展

`Navigation` 至少链接 `RESEARCH.md` 和该 Study 实际执行的 canonical Design。后续 Dataset 可以通过 `study/README.md` 索引或 Research Tree 反向发现，不为了新 Dataset 改写已经完成的历史实施事实。Sample、Assay、deviation、batch 等可在相应 H2 下用 H3+ 按对象展开，数量不受机械限制。

`Record Boundary / Corrections` 必须保持证据来源层级；任何追溯性补充必须说明依据，不能把推断包装成现场直接记录。

## 缺失状态

温度、时间、Sample identity、instrument setting 或其他关键事实不明确时使用 `未记录`、`未知` 或 `待确认`，不得从上下文猜值。某类事件真实未发生时写 `不适用：<原因>`。

## 目录索引

`study/README.md` 固定为：

```markdown
# Studies

## Objects

- [<title>](<slug>/README.md) — <in-progress/completed/aborted 与最短实施说明>

## Relations

- [<Study>](<slug>/README.md) → [<Design>](../designs/<design-slug>.md), [<Dataset>](../data/<dataset-slug>/README.md)
```

`Objects` 覆盖全部已登记 Study。`Relations` 保存当前数据库已知的上游 Design 与下游 Dataset；当前没有已登记关系时显式写 `不适用：当前没有已登记的相关人类科研对象。`。该可更新索引承担后续 Dataset 等对象的反向发现。

## 合格示例

一次测序 Study 可以在 `Assays and Measurements` 下用多个 H3 记录 extraction、library preparation 与 sequencing run，并把 lane / run 放入 `Batch / Run / Time`；若某个 Sample 丢失，明确写入 `Failures / Missing Events` 而不是从后续数据表中静默消失。

## 代表性错误

把 `study/README.md` 同时当作某个 Study 正文和目录索引；删除没有 deviation 的 `Deviations` 章节；把实际偏离回写 frozen Design；用推断值补空缺仪器参数；Navigation 指向 `.research/`；目录索引漏掉已登记 Study。

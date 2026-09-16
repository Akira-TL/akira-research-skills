---
name: review-revision
description: 对修回稿、修订分析、Figure、Supplement 与 response letter 执行 evidence-before-persuasion 再审；用于已有 original concern / editor decision 与 resolution criterion，需要判断修订是否真实解决问题、是否通过合理降低 Claim 闭合，或是否产生新的科学问题时。
---

# Review Revision

`review-revision` 负责 Review series 的再审闭环。它判断修订后的真实 manuscript / evidence 是否达到原 concern 的解决条件；response letter 是最后核对的说明材料，不是“问题已解决”的证据来源。

## 1. 冻结原问题与原解决条件

先读取 original concern / editor decision、原 manuscript（需要时）与当时明确的 resolution criterion。把原问题复述成可检查条件，并在查看作者 response letter 前冻结。

若原 concern 自身缺少可验收的 resolution criterion，先根据原 concern 的科学含义重建最窄可检查条件，并明确这是 Reviewer 对原问题的操作化，不把修回后的结果倒灌回原标准。

完成标准：每个待再审 concern 都有固定的 target Claim / section、原科学后果与 resolution criterion。

## 2. 先检查真实修订 artifact

按 evidence-before-persuasion 顺序检查 revised manuscript、Analysis、Figure / Table、Supplement、code / data 或用户明确加入 Review Packet 的其他真实 artifact。需要时与 original version 对比，确认实际发生了什么变化。

先独立回答：

- 修订是否真实存在；
- 新 evidence 是否与 concern 指向同一问题；
- 当前 evidence 是否满足原 resolution criterion；
- Claim、scope、uncertainty 是否随新 evidence 正确改变；
- 是否产生新的科学问题。

作者“说已经完成”与 artifact “证明已经完成”保持分离。

## 3. 判定当前状态

每个原 concern 至少使用以下状态之一：

- **已解决**：真实修订满足原 resolution criterion；
- **部分解决**：解决了部分科学缺口，但仍有原 criterion 未满足；
- **未解决**：关键缺口仍然存在；
- **作者通过合理降低 Claim 闭合**：未建立原更强 Claim 所需 evidence，但通过缩窄 inference / scope 使现有稿件重新与 evidence 匹配；
- **新证据改变原问题**：新的真实 evidence 使原 concern 的科学前提发生实质变化，需要基于新状态重新判断；
- **当前仍无法判断**：必要修订材料或 evidence 未提供，不能可靠判定。

新问题可以形成新的 Concern，但必须与“原 concern 是否达到原 resolution criterion”的判断分开，不得用新问题覆盖原状态。

## 4. 最后读取 response letter

只有先形成 artifact-based status 后才读取 response letter。检查作者回复是否：

- 准确描述真实修改；
- 指向实际存在的 manuscript / evidence locator；
- 没有把部分解决表述成完全解决；
- 没有把未完成的 Analysis / Experiment 写成已完成；
- rebuttal reasoning 与当前 evidence 一致。

若 response letter 指向此前遗漏的真实 artifact，可以回到该 artifact 重新检查；最终状态仍由 manuscript / evidence 决定。

## 5. 保持 Claim 与 Scope 纪律

再审继续遵守 `review-science` 的 Claim → Evidence 边界和 **严在 Claim，克制在 Scope**。第二轮 Review 不自动意味着作者必须做更多实验；只要求原 concern 对当前 Claim 真正必要的 resolution。

若作者通过缩窄 Claim 已诚实解决原 validity mismatch，应按“作者通过合理降低 Claim 闭合”记录，而不是坚持原本更强 evidence option。

## 6. 返回再审结果

输出至少包含：

`Original Concern → Original Resolution Criterion → Revised Evidence / Locator → Current Status → Reasoning → Response-letter accuracy → New Concern（若有）`

完成标准：每个原 concern 的当前状态都由真实修订 artifact 支撑，response letter 只承担核对作用，新 concern 与原 concern 状态分离。
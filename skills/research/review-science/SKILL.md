---
name: review-science
description: 从学术评议者视角检查研究材料中的 Claim → Evidence / Experiment / Analysis → assumptions → alternative explanation → supported inference 链；用于判断 Design、Analysis、推断层级、scope、reproducibility 与 evidence sufficiency，并形成可定位、可验收的 Major / Minor Concern。
---

# Review Science

`review-science` 负责 Review series 的核心科学有效性评议。它不负责作者侧 Interpretation，不修改 canonical Claim，也不把 checklist 数量当作科学严格性。

## 1. 建立 Claim chain

从 `akira-review` 已重建的 Research Question、Claims、decisive evidence 与 Assessment Boundary 出发。对每个会改变稿件主要结论的 Claim，按 [`references/SCIENTIFIC-ASSESSMENT.md`](references/SCIENTIFIC-ASSESSMENT.md) 重建：

`Claim → Evidence / Experiment / Analysis → necessary assumptions → alternative explanations → supported inference`

完成标准：能明确指出当前 evidence 真正支持到哪一层，以及 Claim 是否越过 Design、measurement 或 Analysis 能提供的 inference level。

## 2. 审查实际适用的科学维度

只审查与当前 Claim 和材料真实相关的维度，包括但不限于：

- Research Question 与 estimand / target quantity 是否一致；
- sampling、comparison、controls 与 internal validity；
- measurement validity 与数据生成过程；
- statistical / computational Analysis 是否识别目标 Claim；
- uncertainty、robustness、sensitivity 与可重复性；
- association、causality、mechanism、process 等 inference level；
- population / system / condition 的 external validity 与 scope；
- competing / alternative explanation 是否仍与 evidence 兼容。

没有证据需求的维度不为凑数量强行生成问题。

## 3. 重建隐藏前提

对 Claim 成立所依赖但稿件未显式写出的关键前提，按以下状态表达：

- 已支持；
- 合理但未验证；
- 当前不支持；
- 当前无法判断。

只有会改变 Claim truth、scope 或 interpretation 的前提才升级为实质 Concern。

## 4. 形成 Concern

所有实质问题按 [`references/CONCERNS.md`](references/CONCERNS.md) 形成可定位、可解释、可验收的 Concern。严重度默认使用 Major Concern / Minor Concern；一个问题若会使 central Claim 无法成立，应在 scientific consequence 中直接说明，不额外创造总分或新严重度体系。

Review 的原则是：**严在 Claim，克制在 Scope**。对 Major Concern 区分当前 Claim 成立所需的 minimum honest remedy 与支持更强 Claim 的 optional stronger evidence；如果降级 Claim 就能诚实闭合，不默认要求新实验。

完成标准：每个 Major Concern 都能说明影响哪个 Claim、依据在哪里、为什么重要、科学后果是什么，以及怎样才算解决。

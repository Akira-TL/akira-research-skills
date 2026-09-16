# Concern Contract

Concern 是 Reviewer 对某个科学问题的可定位判断，不是泛化意见清单。

## Required fields

每个实质 Concern 至少表达：

- **Concern**：问题本身；
- **Target Claim / section**：被影响的 Claim 或 manuscript 区域；
- **Evidence locator**：稿件、Figure、Table、Analysis 或其他当前材料中的定位；
- **Assessment**：Reviewer 当前判断；
- **Why it matters**：为什么这一点影响科学有效性；
- **Scientific consequence**：它会怎样改变 Claim truth、inference level、scope 或 uncertainty；
- **Severity**：Major Concern 或 Minor Concern；
- **Confidence**：Reviewer 对该判断的把握及其限制；
- **Resolution criterion**：什么证据或修改能够证明问题已经解决。

若当前 Review 尚未完成 literature verification，Concern 不得把模型记忆当 citation；只有在外部证据真实核验后，才能把相应文献作为关键依据并加入 locator。

## Major vs Minor

**Major Concern**：若不解决，会实质改变 central Claim、主要 inference、关键 scope、可信度或稿件核心科学解释。

**Minor Concern**：需要澄清、补充或修正，但在当前证据边界内不会改变主要科学结论。

不设置问题数量配额，也不通过总分或加权分数汇总科学有效性。

## Remedy discipline

对 Major Concern 区分：

- **Minimum honest remedy**：使当前稿件的 Claim 与已有 evidence 重新匹配所需的最低修复；
- **Optional stronger evidence**：只有作者希望保留更强 Claim 或扩大 scope 时才需要的额外 evidence；
- **No honest remedy in current material**：当前材料无法支撑该 Claim 时，明确要求撤回、降级或重新研究，而不是靠措辞掩盖。

例如 observational evidence 被写成 causal Claim 时，若当前研究并未识别 causality，minimum honest remedy 可以是把 Claim 降级到 association；额外 intervention / identification evidence 属于保留更强 causal Claim 的方案，不自动成为当前稿件必须新增的实验。

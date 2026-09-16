---
name: akira-review
description: 对研究故事、outline、部分或完整手稿、Figure/Table 等材料进行学术评议；先固定当前可评议边界并重建稿件的 Research Question、Claims、decisive evidence 与 scope，再调用 Review series 的专业 Skill 判断科学有效性。用于用户明确要求导师式看稿、学术评议、审稿或独立检查研究论证时。
disable-model-invocation: true
---

# Akira Review

`akira-review` 是 Review series 的顶层 Router。它负责确定本轮评议材料与可评议边界、重建稿件的科学主张、调用专业 Review Skill，并把结果组织成对用户可行动的学术评议；它不拥有作者侧 canonical scientific state，也不替作者执行修改。

## 1. 固定评议材料与边界

接受研究故事、outline、Abstract、部分 manuscript、Figure / Table、完整 manuscript 或其他用户明确提供的研究材料。材料不完整时继续评议当前可见部分，不把“未提供”解释成“作者未完成”。

先按 [`references/REVIEW-BOUNDARY.md`](references/REVIEW-BOUNDARY.md) 形成 Assessment Boundary：本轮看到了什么、哪些信息缺失、哪些判断因此可作、哪些只能保持 Not Assessable。

完成标准：后续每个实质判断都能说明它基于哪些已提供材料，且没有把缺失输入转写成作者缺陷。

## 2. 先重建，再批评

在形成 Concern 前，先从材料中重建：

- Research Question；
- central Claim 与 secondary Claims；
- decisive evidence 及其定位；
- population / system / scope；
- 当前稿件实际讲述的科学故事；
- 当前不可判断部分。

如果作者表达的目标故事与材料中能够重建的故事不同，分别写清“作者当前声称什么”和“当前材料实际支持什么”，不要先替作者修正故事再评价。

完成标准：能够用最窄表述复述 central Claim、最强证据与关键 scope，而不依赖作者自我评价词汇。

## 3. 建立外部文献参照

只要本轮需要判断 novelty、priority、scientific contribution、closest prior work、方法先例或与当前 Claim 直接冲突的既有证据，先调用 [`review-literature`](../review-literature/SKILL.md)。它负责建立 bounded field frame、寻找 closest prior work、按判断责任提升阅读深度，并返回可核验的 contribution / novelty judgment。

作者 Introduction 与 reference list 只能作为检索起点；没有完成外部文献核验时，novelty / priority 主张保持**待文献核验**，不得仅凭模型记忆或作者措辞作强判断。

完成标准：任何实质 novelty / priority / contribution 判断都有可核验的 prior-work basis；“未发现先例”带明确检索边界。

## 4. 路由科学评议

需要判断 Claim 是否被当前设计、数据、分析与推断链支持时，调用 [`review-science`](../review-science/SKILL.md)。文献定位先于需要它支撑的 novelty / contribution 判断，但不替代对 Design、Analysis 与 Evidence → Claim 的独立科学审查。

## 5. 组织基础导师式评议

基础输出按 [`references/REPORTING.md`](references/REPORTING.md) 组织，至少回答：

1. 我对这个工作的理解；
2. 当前最强证据与真正有价值的部分；
3. 当前最大的科学脆弱点；
4. 当前最优先需要解决的科学问题；
5. 其余 Major / Minor Concern 与 Not Assessable 项。

Review 的默认终点是判断与 Concern，不自动进入 revision、Analysis、Study 或 Communication。

完成标准：输出能够把“稿件当前讲的故事”和“当前材料最强能够支持的故事”区分开，并把每个重大问题连接到明确的科学后果和解决条件。

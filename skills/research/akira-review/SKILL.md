---
name: akira-review
description: 对研究故事、outline、部分或完整手稿、Figure/Table 等材料进行学术评议；先固定当前可评议边界并重建稿件的 Research Question、Claims、decisive evidence 与 scope，再调用 Review series 的专业 Skill 判断科学有效性。用于用户明确要求导师式看稿、学术评议、审稿或独立检查研究论证时。
disable-model-invocation: true
---

# Akira Review

`akira-review` 是 Review series 的顶层 Router。它负责确定本轮评议材料与可评议边界、重建稿件的科学主张、调用专业 Review Skill，并把结果组织成对用户可行动的学术评议；它不拥有作者侧 canonical scientific state，也不替作者执行修改。

## 1. 选择 Review Mode 并固定 Review Packet

接受研究故事、outline、Abstract、部分 manuscript、Figure / Table、完整 manuscript 或其他用户明确提供的研究材料。材料不完整时继续评议当前可见部分，不把“未提供”解释成“作者未完成”。

先按 [`references/REVIEW-BOUNDARY.md`](references/REVIEW-BOUNDARY.md) 区分 **independent review** 与 **project-informed mentor review**，再固定本轮 **Review Packet** 和 Assessment Boundary。Independent review 只读取本轮明确提供或允许的材料；project-informed mentor review 只有用户明确授权后才把指定 Research context 加入 Review Packet，并在输出中如实标明模式。

若材料属于真实第三方未发表期刊同行评议，必须在处理全文前先执行 [`references/CONFIDENTIALITY.md`](references/CONFIDENTIALITY.md) 的 confidentiality / generative-AI policy gate；政策未核验、禁止或缺少所需授权时 fail closed。用户自己的稿件、用户明确有权提供的材料与投稿前模拟 Review 不进入这一第三方 gate。

完成标准：Review Mode、Review Packet、实际可见材料、缺失材料、Assessable 与 Not Assessable 均已明确；后续每个实质判断都能说明它基于哪些获准材料，且没有把缺失输入转写成作者缺陷。

## 2. 识别修回再审

如果本轮输入包含 original concern / editor decision、revised manuscript 或其他修订 evidence，并且目标是判断问题是否真正解决，直接调用 [`review-revision`](../review-revision/SKILL.md)。再审不要求用户先进入 Communication，也不把 response letter 作为起点。

完成标准：修回 / 再审意图已经路由到 `review-revision`，原 concern 的 resolution criterion 在读取作者说服性回复前得到固定。

## 3. 先重建，再批评

在形成 Concern 前，先从材料中重建：

- Research Question；
- central Claim 与 secondary Claims；
- decisive evidence 及其定位；
- population / system / scope；
- 当前稿件实际讲述的科学故事；
- 当前不可判断部分。

如果作者表达的目标故事与材料中能够重建的故事不同，分别写清“作者当前声称什么”和“当前材料实际支持什么”，不要先替作者修正故事再评价。

完成标准：能够用最窄表述复述 central Claim、最强证据与关键 scope，而不依赖作者自我评价词汇。

## 4. 建立外部文献参照

只要本轮需要判断 novelty、priority、scientific contribution、closest prior work、方法先例或与当前 Claim 直接冲突的既有证据，先调用 [`review-literature`](../review-literature/SKILL.md)。它负责建立 bounded field frame、寻找 closest prior work、按判断责任提升阅读深度，并返回可核验的 contribution / novelty judgment。

作者 Introduction 与 reference list 只能作为检索起点；没有完成外部文献核验时，novelty / priority 主张保持**待文献核验**，不得仅凭模型记忆或作者措辞作强判断。

完成标准：任何实质 novelty / priority / contribution 判断都有可核验的 prior-work basis；“未发现先例”带明确检索边界。

## 5. 路由科学评议

需要判断 Claim 是否被当前设计、数据、分析与推断链支持时，调用 [`review-science`](../review-science/SKILL.md)。文献定位先于需要它支撑的 novelty / contribution 判断，但不替代对 Design、Analysis 与 Evidence → Claim 的独立科学审查。

## 6. 组织评议输出

按 [`references/REPORTING.md`](references/REPORTING.md) 选择导师式学术评议或正式同行评议呈现。用户要求多个审查视角时读取 [`references/MULTI-PASS.md`](references/MULTI-PASS.md)：所有 pass 共用冻结的 Review Packet；只有真实相互隔离的 context 才称 independent / blinded passes，同一 context 的多轮只能称 multi-lens review；个体报告先冻结再综合，consensus 不替代科学判断。

Reviewer 默认不输出最终编辑决定。只有用户明确要求、真实 target venue 当前确实要求 Reviewer recommendation，且对应 reviewer instructions 已核验时，才按该 venue 的当前选项提供 reviewer-facing recommendation；最终 editorial decision 仍属于 Editor / editorial team。

Review 的默认终点是判断与 Concern，不自动进入 revision、Analysis、Study 或 Communication。

完成标准：输出与 Review Mode 一致，能够把“稿件当前讲的故事”和“当前材料最强能够支持的故事”区分开，并把每个重大问题连接到明确的科学后果和解决条件。

## 7. 只通过显式 Handoff 返回 Research

若 Concern 需要新增 Literature、Analysis、Interpretation、Design / Study / Data 或纯表达修改，按 [`references/HANDOFF.md`](references/HANDOFF.md) 返回 resolution criterion 与建议 route，然后停止。只有用户决定采纳后，才交给 `akira-research` 改变 canonical scientific state 或交给 `communication` 修改稿件；Reviewer 本身不直接修改这些作者侧事实源。

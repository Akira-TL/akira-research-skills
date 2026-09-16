# akira-review

`akira-review` 是 Akira Research Skills 中与 `akira-research` 平级的第二个顶层 Router，用于导师式学术评议、手稿科学审查以及后续扩展的正式同行评议。它接受研究故事、outline、部分 manuscript、Figure / Table 或完整稿件，不要求用户先准备完整 submission package。

## 工作方式

Review 先选择模式并固定 Review Packet。**Independent review** 只读取本轮明确提供或允许的材料，不因为与 Research project 同仓就自动读取 `RESEARCH.md`、Research database、内部 Interpretation、未提交结果、planning 或 prior AI review；**project-informed mentor review** 只有用户明确授权后才把指定 Research context 加入评议，并在输出中如实标明这是项目知情的导师式评议。

随后建立 Assessment Boundary：记录本轮实际看到的材料、缺失材料、当前可判断内容与 Not Assessable 内容，再重建 Research Question、central / secondary Claims、decisive evidence、population / system / scope 和稿件实际讲述的科学故事。

需要判断 novelty、priority、scientific contribution、closest prior work 或方法先例时，先调用 `review-literature` 建立外部文献参照并核验最近邻工作；再由 `review-science` 检查 Claim 与 evidence 是否匹配。作者 Introduction 与 reference list 只是文献核验起点，不能代替独立检索。

真实第三方未发表期刊稿件在处理全文前还要核验目标 journal / publisher 当前的 confidentiality 与 generative-AI policy；政策未核验、禁止或缺少所需授权时停止全文 AI Review。用户自己的稿件、明确有权提供的材料和投稿前模拟 Review 不被这一第三方 gate 自动阻塞。

## 输出方式

导师式学术评议优先说明 Reviewer 对工作的理解、当前最强 evidence 与真实贡献、稿件故事与材料最强可支持故事之间的差异、主要科学脆弱点和优先科学问题。

正式同行评议使用总体评价、Major Concerns、Minor Concerns、必要的创新性 / 文献定位与 Not Assessable。不会为模拟真实审稿外观凑固定数量的问题，也默认不输出 Accept / Reject / Major Revision 等最终编辑决定；只有用户明确要求且目标 venue 当前 reviewer workflow 实际要求 reviewer recommendation 时才按其官方规则提供。

多视角 Review 先冻结共同 Review Packet 和各自 review lens。只有真实相互隔离的 context 才称 independent / blinded review；同一 context 的多轮只能称 multi-lens review。个体报告先冻结再综合，consensus 不作为科学真值或投票结论。

`akira-review` 默认停在学术判断与 Concern，不直接修改作者的 canonical scientific state、分析或稿件。

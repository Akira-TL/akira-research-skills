# review-literature

`review-literature` 为 Reviewer 建立有边界的领域参照、closest prior work 与 contribution / novelty 判断。它解决的是“为了评议这份稿件，现在必须核验哪些已有研究”，而不是启动完整 Literature Research。

## 工作方式

Reviewer 先从稿件的 Research Question、对象、核心关系 / 现象、干预 / exposure、measurement、method operation 与 central Claim 拆出检索概念，再补充同义术语、既有分类和相邻方法。作者 reference list 只是起点；需要独立检索最近邻工作，并在必要时沿 backward / forward citation network 继续核验。

对 `first`、`novel`、`previously unknown`、方法首创等强声明，要主动搜索最可能推翻该声明的工作。任何承担“别人已经做过”“prior method 本质相同”“central Claim 已被直接证明 / 反驳”“已知方法局限构成 Major Concern”等重要判断责任的 prior work，都必须阅读到足以独立核验判断的原始内容深度。

## 输出边界

contribution assessment 不使用 novelty score，而是比较已有知识、当前真实增量、作者声称但尚未建立的 novelty，以及可能被作者低估的真实贡献。“未发现先例”必须带当前数据库、检索概念、日期与引文链等边界。

该 Skill 可以调用 `literature-access` 取得已确定论文的全文或 Supplement，并在需要当前正式规范时调用 `research-standards`；默认不创建 Research Search Run、Candidate、Paper、reading queue、human literature note、`RESEARCH.md` 或 `research.sqlite` 状态。若用户决定把相关文献纳入自己的科研项目，再交回 `akira-research → literature`。

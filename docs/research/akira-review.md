# akira-review

`akira-review` 是 Akira Research Skills 中与 `akira-research` 平级的第二个顶层 Router，用于导师式学术评议、手稿科学审查以及后续扩展的正式同行评议。它接受研究故事、outline、部分 manuscript、Figure / Table 或完整稿件，不要求用户先准备完整 submission package。

## 第一版工作方式

Review 先建立 Assessment Boundary：记录本轮实际看到的材料、缺失材料、当前可判断内容与 Not Assessable 内容。随后先重建 Research Question、central / secondary Claims、decisive evidence、population / system / scope 和稿件实际讲述的科学故事，再调用 `review-science` 检查 Claim 与 evidence 是否匹配。

当前第一版尚未包含独立的文献定位与创新性核验闭环，因此 novelty、priority、"首次"等判断在没有外部文献核验时只能标记为待核验，不能把作者自己的表述当作已证实事实。

## 默认输出

基础导师式评议优先回答：

- Reviewer 对工作的理解；
- 当前最强 evidence 与真正有价值的部分；
- 稿件当前讲的故事与材料最强能够支持的故事是否一致；
- 当前最大的科学脆弱点；
- 最优先应解决的科学问题；
- 其余 Major / Minor Concern 与 Not Assessable 项。

`akira-review` 默认停在学术判断与 Concern，不直接修改作者的 canonical scientific state、分析或稿件。

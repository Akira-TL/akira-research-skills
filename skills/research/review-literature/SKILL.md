---
name: review-literature
description: 为学术评议建立有边界的领域参照、closest prior work 与 contribution / novelty 判断；在 Reviewer 需要核验已有工作、创新性、priority、方法先例或与当前 Claim 直接冲突的外部证据时使用，不创建完整 Research Literature 项目状态。
---

# Review Literature

`review-literature` 负责 Reviewer 所需的 **bounded scholarly verification**。目标不是完成系统综述或 Research Literature completion gate，而是取得足够、可核验的外部参照，回答：已有知识到了哪里，最接近的既有工作是什么，当前稿件真正新增了什么。

## 1. 从稿件主张定义核验目标

从 `akira-review` 已重建的 Research Question、central Claims、claimed contribution 与 Assessment Boundary 出发，只建立会影响当前评议判断的文献问题。

把 novelty / priority 主张按科学实质拆成：研究对象、核心现象或关系、干预 / exposure、measurement、method operation、central Claim。检索时扩展规范同义词、既有分类和相邻术语；新的命名本身不视为新的方法或科学对象。

## 2. 建立 field frame 与 closest prior work

按 [`references/LITERATURE-NOVELTY.md`](references/LITERATURE-NOVELTY.md) 执行三层工作：

1. field calibration：确认领域基本问题、主流术语与代表性工作；
2. closest-prior-work search：从作者引用之外独立搜索最接近的 Research Question、方法、population / system 与 Claim；
3. citation-network check：围绕最近邻工作做必要的 backward / forward citation chasing。

作者 reference list 只是起点，不是 novelty 判断的边界。对 `first`、`novel`、`previously unknown`、方法首创等强声明，主动设计至少一轮可能推翻该声明的检索。

## 3. 按判断责任决定阅读深度

普通领域校准可以使用 review、metadata、abstract 和代表性论文的相关部分；越接近核心 judgment，阅读越深。

凡某篇 prior work 将承担以下判断之一，必须取得并检查足以独立核验判断的原始内容：

- 当前工作已经有人直接做过；
- prior method 与当前方法本质相同；
- central Claim 已被直接证明或反驳；
- 主要 innovation 只是增量变化；
- 已知方法局限构成 Major Concern；
- 关键既有证据直接改变当前稿件的解释。

已知目标论文需要全文或 Supplement 时调用 `literature-access`。适用的正式 guideline / standard 需要当前权威来源时调用 `research-standards`，不要把普通论文当成规范本身。

## 4. 判断真实 contribution

不要输出 novelty score。比较已有知识与当前工作，至少区分：

- 已有工作已经建立的内容；
- 当前稿件真实新增的知识、证据或边界；
- 作者声称为 novelty 但尚未建立的部分；
- 作者可能低估、但当前材料与 prior work 比较后真实存在的贡献。

核心问题是：**在已有知识状态下，这篇稿件增加了什么此前不能可靠知道的东西？**

“未发现先例”只能写成受当前数据库、检索概念、日期、语言与引文链限制的 bounded conclusion，不能升级为“从未有人做过”。

## 5. 返回 Review，不写 Research Literature state

向 `akira-review` 返回 field frame、closest prior work、已核验的关键比较、真实 contribution / novelty judgment、未闭合检索边界与必要 citation locator。

默认不创建或修改 Research Search Run、Candidate、Paper、reading queue、human literature note、`RESEARCH.md` 或 `research.sqlite`。若用户决定把这些文献正式纳入自己的科研项目，再交回 `akira-research → literature` 建立 canonical Literature state。

完成标准：任何会改变 novelty、priority、主要 contribution 或重大文献型 Concern 的判断都有可核验外部依据；未找到先例的结论保留明确检索边界。

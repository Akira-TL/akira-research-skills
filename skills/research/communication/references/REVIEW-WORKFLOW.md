# 普通文献综述写作流程

本文件约束叙述性文献综述（Narrative Review）及其他以既有文献的组织、比较、批判和综合为主要贡献的普通综述。正式起草前先按 [`SCIENTIFIC-WRITING-CONTRACT.md`](writing/SCIENTIFIC-WRITING-CONTRACT.md) 建立稿件术语表与贡献类型；生物学与生物信息学分别叠加 [`context/BIOLOGY-WRITING.md`](context/BIOLOGY-WRITING.md) 或 [`context/BIOINFORMATICS-WRITING.md`](context/BIOINFORMATICS-WRITING.md)。系统综述（Systematic Review）、范围综述（Scoping Review）与荟萃分析（Meta-analysis）不得直接使用本流程替代其正式科研方法；类型边界见 [`WRITING-ROUTER.md`](WRITING-ROUTER.md)。

普通综述的价值不在于“引用很多论文”，而在于让读者看清：这个问题已经知道什么、不同研究路线如何关联、为什么出现一致或冲突结果、哪些边界仍未解决，以及下一步真正值得研究什么。

## 1. 先固定 Review Question、Scope 与边界

开始正文前先写清这篇综述到底“综什么”。主题不能只停留在宽泛领域名称，应形成可以约束材料选择和正文结构的 Review Question / Scope。

至少明确：

- 核心问题或核心主题；
- population / system / phenomenon；
- 纳入讨论的方法、机制、理论或应用范围；
- 明确不讨论什么；
- 需要时说明时间、地域、物种、数据类型或研究设计边界；
- 这篇综述希望解决的主要认知困难：领域结构不清、结果冲突、方法不可比、理论分裂、机制链缺失或其他真实 uncertainty。

普通综述可以采用目的驱动的 literature discovery，但不得因为写作方便伪装成“穷尽了全部文献”。只有完成相应正式方法学流程时，才能声称 systematic / exhaustive search。

## 2. 先完整盘点综述材料，不直接开始按论文写正文

正文前默认维护 `REVIEW-MATERIALS.md` 或等价材料清单。它是 Communication 阶段从 `research.sqlite`、原始论文和 Literature evidence 派生的导航，不是新的科学事实源。

在既定 Scope 内主动检查：

- foundational / seminal work；
- 代表性研究；
- 近期关键工作；
- 不同理论路线；
- 不同方法路线；
- 支持、一致、限定和冲突证据；
- negative / null evidence；
- population、measurement、design、analysis 等边界条件；
- 失败、不可重复或结果不一致的应用；
- 重要 review / perspective；
- 关键 dataset、method、resource；
- 尚未解决的 uncertainty。

**材料层要尽可能全面，正文层可以有主次。** 不能只保留支持某个预设观点的论文；重要冲突路线、反证和边界必须进入材料视野。普通综述不必在正文逐篇展开所有材料，但重要材料应能说明最终被放入哪个主题、表格、图示、补充部分或仅作为背景核验。

综述和学位论文中的综述章节可以用于建立领域地图、术语和引用链；关键科学判断尽量回到原始研究核验。Agent sidecar、搜索摘要和二手转述不能替代正式 citation source。

## 3. 先建立问题导向的组织骨架

综述正文的基本单位应是**问题、主题或证据类别**，不是“Paper A / Paper B / Paper C”。除非写作目的本身是历史发展史，否则不按作者或年份逐篇罗列。这里的“组织骨架”只是对已有领域对象和问题做排序，不要求创造新的 taxonomy、层级名称或 framework。

可根据研究对象选择一个或多个已有学术维度：

- Research Question；
- mechanism / pathway；
- theory；
- method / measurement；
- population / system；
- application context；
- result / evidence type；
- controversy / unresolved issue；
- historical stage。

组织维度必须帮助回答 Review Question。若现有领域术语已经足够，直接使用它们；不要为了让目录显得复杂或体现“综述贡献”而重新命名已有类别。

写完整 prose 前，默认维护 `REVIEW-OUTLINE.md` 或等价提纲，例如：

```text
Review Question / Scope
→ 主题 1
   → 已知什么
   → 主要方法/理论
   → 一致证据
   → 冲突证据
   → 边界
→ 主题 2
   → ...
→ 跨主题关系
→ 理论 / 概念框架
→ 真实 gap / unresolved question
→ future direction / review contribution
```

## 4. 每个主题都做跨论文综合，不做摘要拼接

一个主题小节不能只是连续写：

```text
A 发现……
B 发现……
C 又发现……
```

而应回答：

1. 这一主题当前最稳定的共识是什么；
2. 哪些研究支持这一判断；
3. 哪些研究得到不同或冲突结果；
4. 差异是否可以由 population、design、measurement、analysis、context 或时间阶段解释；
5. 哪些差异仍然无法解释；
6. 当前 evidence 能支持到什么层级；
7. 这一主题如何引出下一个主题。

推荐写法是“综合判断 → 代表性证据 → 冲突/边界 → 原因比较 → 当前最窄结论”，而不是把每篇论文各缩写一遍。

引用簇必须承担明确综合任务。不要用一个长 citation list 代替比较；若多篇论文实际上支持不同条件下的不同结论，应在句子中明确拆开。

## 5. 先做跨主题综合，框架只是可选产物

完成各主题后，先用普通领域语言回答：

- 哪些结论跨研究相对稳定；
- 哪些差异可以由 population、design、measurement、analysis 或 context 解释；
- 哪些冲突仍未解决；
- 不同主题之间真正共享什么机制、条件或 uncertainty。

只有当这些关系已经由 literature evidence 建立，而且图示或框架能明显降低读者理解成本时，才考虑 mechanism map、evidence map、timeline 或 conceptual model。已有文献存在成熟理论 / 分类时优先沿用并正确引用；需要提出作者自己的 conceptual synthesis 时，必须明确它是 synthesis，而不是领域既有术语。

若还需要为这个 synthesis **新命名**，返回 [`SCIENTIFIC-WRITING-CONTRACT.md`](writing/SCIENTIFIC-WRITING-CONTRACT.md) 的新术语四道门槛；Communication 不能因为“综述应该有框架”而自行创造名称。

## 6. 从综合结果推出真正的研究缺口

综述中的 gap 不能只写“关于 X 的研究较少”“目前鲜有报道”。优先判断：

- 哪个关键问题仍无法回答；
- 为什么现有研究无法回答；
- 是样本、measurement、design、analysis、理论还是证据冲突造成；
- 新研究需要什么样的判别性 evidence 才能缩小 uncertainty。

如果只是“数量少”但已有 evidence 足以回答核心问题，就不能人为制造 gap。相反，论文数量很多也不代表问题已经解决；若方法不可比、研究共享数据、关键边界从未测试或结果长期冲突，仍可以形成真实 unresolved question。

Future direction 必须对应前面已经论证的 gap，不得在结尾突然列出与正文无关的愿望清单。

## 7. 明确综述自己的贡献

在已有文献综合之后，再说明这篇综述额外提供了什么。可能包括：

- 用已有领域维度更清楚地组织复杂 evidence；
- 揭示不同理论或方法真正的分歧点；
- 解释表面冲突由哪些研究条件造成；
- 区分已经较稳定的知识与仍未解决的问题；
- 发现不同研究之间缺失的关键连接；
- 在 evidence 足够时形成明确标注的 conceptual synthesis；
- 给出针对真实 uncertainty 的 future research priorities。

综述贡献必须从前面的材料和综合推出，不能因为需要“创新点”而临时创造一个概念。

## 8. 图表优先表达跨论文关系

普通综述尤其适合使用能够压缩跨论文关系的 Figure / Table，例如 evidence matrix、comparison table、timeline、mechanism diagram 或 controversy / gap map。只有现有领域分类或当前 evidence 真正需要时才使用 taxonomy table / conceptual model；不要为了形成一张“综述框架图”而新造分类名称。

表格和图示应帮助读者比较研究，而不是重复正文。每一个重要图表都应能回到具体 Paper / Observation / relation，不能画出比已有 evidence 更确定的机制链。

## 9. 正文起草顺序

普通综述不采用原始研究论文的“主要结论 → Results → Discussion”流程。推荐顺序是：

```text
Review Question / Scope
→ 完整材料盘点
→ 问题导向的组织骨架
→ 各主题跨论文综合
→ 跨主题综合（必要时形成可选 conceptual model）
→ gap / unresolved question
→ future direction / review contribution
→ 搭正文 outline 与主要 Figure / Table
→ 起草各主题正文
→ 最后写 Introduction、Conclusion、Abstract、Title
```

Introduction 最后写，是为了让它准确建立正文实际处理的范围、问题和组织方式，而不是先写一个过大的领域背景再勉强填正文。

## 10. 综述的大逻辑审查

全文完成后至少检查：

- Review Question 与 Scope 是否清楚；
- 问题导向的组织骨架是否真的服务核心问题；
- 各主题是在综合还是仍然逐篇罗列；
- 主题顺序是否有知识或推理上的推进关系；
- 是否同时处理了一致、冲突和限定 evidence；
- 若使用 theoretical / conceptual model，它是否确有必要并忠实于已有 evidence；
- gap 是否由前文分析真正推出；
- future direction 是否对应真实 gap；
- Conclusion 是否概括跨论文 synthesis，而不是再次罗列作者；
- 是否有一整类重要研究路线、反证或边界被遗漏；
- 是否把普通叙述性综述写成了未经正式方法支持的“系统综述”。

小逻辑、段落衔接、连接词和结论强度继续按 [`WRITING-EXPRESSION.md`](WRITING-EXPRESSION.md) 自审。

## 11. 写作中发现材料缺口时返回 Literature

如果写某一主题时发现：前驱工作、后续工作、关键原始论文、冲突 evidence 或方法来源不足，不在 Communication 中凭模型常识补齐。返回 `literature` 完成检索、获取、Reconstruction / Critical Audit 和必要 relation，再回到本流程更新材料清单和 synthesis。

普通综述完成初稿后、进入 reviewer-style review 前执行 [`audit/INTEGRITY-AUDIT.md`](audit/INTEGRITY-AUDIT.md) 初稿审计，重点核验 citation identity、claim-to-source support、scope 与 novelty wording；实质 revision 后在最终交付前再执行最终审计。若修订来自 reviewer / editor comment，同时使用 [`REVISION-WORKFLOW.md`](REVISION-WORKFLOW.md)。

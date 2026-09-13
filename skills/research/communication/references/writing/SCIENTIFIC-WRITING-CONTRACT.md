# 科研论文共同写作契约

本文件定义原始研究论文、普通综述和方法论文共享的**生成习惯**。它不规定某个期刊的固定格式，也不替代具体学科的 reporting guideline。术语是否属于已有学术概念、中文 / 英文标准名称和证据层级继续以 [`ACADEMIC-LANGUAGE.md`](../../../akira-research/references/standards/ACADEMIC-LANGUAGE.md) 为 authority；本文件负责把这些纪律落实到 manuscript 起草过程。目标是让 Agent 从一开始就按成熟论文的方式组织语言，而不是先生成内部化、抽象化 prose，再靠大量负向提示词返工。

## 1. 论文的基本单位是“读者问题 → 证据 → 最窄结论”

正式起草前，先为全文写一句中心贡献，并为每个 section / paragraph 写清它回答的读者问题。

每个段落默认只承担一个主要任务：

- 建立必要背景；
- 说明已有证据；
- 提出尚未解决的问题；
- 说明方法选择；
- 报告一个主要发现；
- 解释该发现；
- 与已有研究比较；
- 说明一个必要边界；
- 综合多项证据。

段落第一句优先直接承担这个任务，后续句子提供证据、数字、比较或解释；段末只有在真实需要时才给最窄结论或自然转向。不要让一个段落同时承担“定义术语、报告结果、讨论机制、辩护 limitation”四种工作。

跨学科中最稳定的结构不是固定章节名称，而是：

```text
问题是什么
→ 已经知道什么
→ 缺什么
→ 本文做了什么
→ 数据/实验显示什么
→ 这些结果支持什么
→ 与已有知识如何连接
→ 边界在哪里
```

## 2. 先判定“贡献类型”，再决定是否需要命名

开始正文前，先把本文主要贡献归入一类或多类：

- 经验性发现（empirical finding）：新的观察、实验或统计结果；
- 方法学贡献（methodological contribution）：新的方法、算法、实验技术或分析方法；
- 资源贡献（resource contribution）：新的 dataset、catalogue、benchmark、software 或 database；
- 证据综合（evidence synthesis）：对既有文献形成新的系统认识；
- 概念性贡献（conceptual contribution）：新的理论、概念框架或可操作定义。

前三类和证据综合的原创性主要来自**数据、设计、方法或综合结果**，通常不需要再创造一个上位概念名来证明创新。

只有当“提出并区分这个新概念本身”确实属于论文核心贡献时，才进入新概念命名流程。Communication 不得为了让论文显得更有理论性，临时为已有现象、measurement、pipeline stage 或 evidence level 造一个名称。

## 3. 写作前建立稿件术语表

长篇 manuscript 起草前，建立一份简短术语表；它只用于写作控制，不进入论文正文。

对预计会反复出现的核心名词逐项分类：

| 类型 | 处理方式 |
| --- | --- |
| 领域已有标准术语 | 直接采用并保持一致 |
| 标准方法 / 数据库 / 软件 / assay 名称 | 使用官方名称 |
| 项目内部字段 / codebook 标签 | 翻译成领域术语或普通描述 |
| 尚无固定名称的现象 | 用描述性句子表达 |
| 项目已正式提出的新方法 / resource / concept | 只有名称和定义已成为 canonical scientific state 时才使用 |

稿件术语表的目标是让一个**不知道 Akira、Research Tree、数据库字段和项目 codebook 的领域研究者**也能直接读懂论文。

如果删除项目内部标签后，一段文字的科学含义就无法成立，说明这段仍依赖内部 ontology，应先重写概念表达，再继续润色。

## 4. 新术语采用四道门槛

任何准备反复使用的新命名、组合词、框架名、轴、层、效应、模式或缩写，在进入 Title、Abstract、Introduction、Results、Discussion、Figure title 前必须同时满足：

1. **已有术语核验**：已经查过最接近的同行评议文献、方法原始论文或权威术语来源，没有足以准确表达当前对象的成熟术语；
2. **贡献必要性**：命名后的对象本身是本文需要读者记住和复用的学术贡献，而不是为了缩短句子或包装已有概念；
3. **可操作定义**：能够明确说明它与相邻概念的边界，以及什么 observation / experiment / analysis 会支持或否定它；
4. **canonical approval**：该名称与定义已经在项目科研状态中由用户明确批准；Communication 不现场发明。

任一条件不满足时，使用已有术语或普通描述性句子。

**命名不是抽象化的奖励。** 如果 sampling、sample processing、reference database、RNA、protein、metabolite、prediction、association、mediation 已经准确，就继续使用这些词。

## 5. 用已发表论文校准“写法”，不用它们提供本项目事实

当以下任一情况出现时，起草长篇 manuscript 前加载 [`context/WRITING-EXEMPLARS.md`](../context/WRITING-EXEMPLARS.md)：

- 新开一篇重要论文或综述；
- 用户明确反馈当前文字“像 Agent”“像 codebook”“不像发表论文”；
- 当前项目跨越生物学与计算方法两个共同体；
- 不确定 Results / Discussion / Review body 应怎样推进。

从最接近当前文稿的 2–4 篇已发表论文中只提取：

- Abstract 的信息顺序；
- Introduction 如何从领域问题进入 gap；
- section heading 的粒度；
- Results / review body 的段落任务；
- Discussion 如何连接 prior art；
- 术语密度与定义位置；
- limitation / reproducibility 放在哪里。

**不模仿原句、不做句式拼贴，也不把 writing reference 当成 scientific evidence。** 当前论文的事实与引用仍回到本项目 canonical evidence 和 Literature source。

## 6. 各章节的共同职责

### Abstract

默认顺序：

```text
为什么这个问题重要 / 还不知道什么
→ 本文做了什么
→ 3–5 个 headline findings
→ 最窄解释或意义
```

Abstract 只保留定义贡献所需要的方法信息和结果，不承担完整 codebook、全部 secondary result 或审稿人预防性辩护。

### Introduction

默认顺序：

```text
具体领域问题
→ 已有研究已经建立什么
→ 仍然不能回答什么 / 当前方法或证据在哪里不足
→ 为什么这个 gap 重要
→ 本文的研究问题、总体方法与具体贡献
```

每个 gap 必须由 prior art 推出；不能为了制造创新点而把成熟领域常识改名后再宣布缺口。

### Methods / Materials and Methods

Methods 的唯一核心任务是让同行理解**研究实际做了什么以及如何复现 / 审查**。

可以详细定义 sample、assay、algorithm、estimator、benchmark、eligibility、parameter 和 implementation；项目内部 validator、审计规则、文件组织和 workflow 只在它们确实属于科研方法时进入主文，其余留在 Supplement / codebook / repository documentation。

### Results

每个 Results 小节优先采用：

```text
headline finding
→ 关键 evidence / estimate / comparison
→ 必要的 secondary evidence / validation
→ 最多一句最窄结果解释或下一问题
```

小标题优先写“发现了什么”，而不是内部框架、分析脚本名称或工作流阶段。正文不逐项朗读 Figure / Table，也不在同一结果段重复 Discussion。

### Discussion

每个主要段落优先采用：

```text
本研究发现
→ 与已有研究的关系
→ biological / methodological interpretation
→ 最多一个必要边界
```

如果一个主要观点已经完整解释过，后文只引用其含义，不重新完整论证。Strengths and limitations 集中承担大多数通用边界，避免全文持续以防御性否定句推进。

### Conclusion

直接回答论文问题，概括最重要的 2–4 个结论和实际意义。Conclusion 不引入新数据、新文献主张或新术语。

### Figure legend

图注负责让图可以独立读懂：panel 内容、符号、group、denominator、unit、统计量 / uncertainty、必要 source。解释“为什么重要”的完整论证留给正文。

## 7. 原创性用“贡献句”表达，不用“新名词”表达

每篇稿件都维护 1–4 条 contribution sentences。每条贡献句必须指向一种可检查的新东西，例如：

- we measured / quantified / estimated ...；
- we identified ... in a prespecified population；
- we developed a method that ...；
- we benchmarked ... against ...；
- we assembled a resource containing ...；
- we synthesized evidence showing ... under ... conditions。

如果所谓 contribution 只能写成“we propose the concept of X”，继续追问：X 是否真的具有新的定义、预测或用途？若没有，回到数据、方法或综合结果表述。

## 8. 写作表面与内部科研系统分层

Akira 内部可以使用 canonical state、provenance、Research Tree、Active Uncertainty、artifact、freeze、validator 等工程术语保证科研过程严谨；面向期刊读者的 manuscript surface 只保留他们理解科学问题所需的学术语言。

内部对象到论文表面的默认转换例如：

```text
Research Tree node       → research question / hypothesis / analysis / finding
artifact                 → dataset / figure / table / analysis output / protocol
provenance               → data source / method record / version history（按上下文）
freeze                    → prespecified / finalized before outcome inspection（仅在确实相关时）
validator rule            → reporting / eligibility / analysis criterion（仅在科研方法需要时）
```

不要把工程系统的严谨性直接翻译成论文术语密度。

## 9. 完稿做一次“去内部化”审查

在语法润色之前，先逐段检查：

1. 这一段的唯一科学任务是什么；
2. 第一关键名词是否是领域研究者熟悉的对象；
3. 是否存在项目内部标签、自己拼出的上位词或为了避免重复而产生的近义术语；
4. 删除内部标签后，科学事实和逻辑是否仍完整；
5. 这一段是否先说 evidence / finding，再给解释；
6. 是否有超过一个主要边界在反复防御同一误读；
7. 当前 claim 是否可以直接追溯到 data / analysis / literature source。

先通过这一层，再进入 [`WRITING-EXPRESSION.md`](../WRITING-EXPRESSION.md) 做句间逻辑、连接词和 claim strength 审查。

## 10. 完成标准

一篇成熟科研稿件应满足：

- 一个不了解项目内部系统的同行可以直接说明论文问题和主要贡献；
- 核心术语来自该领域真实用法，且全文含义稳定；
- Results / review body 的组织单位是 scientific question / finding / evidence synthesis；
- 创新可以用数据、方法、resource 或 synthesis 具体说明；
- 新命名若存在，确实是被验证和定义的核心贡献；
- Methods 负责复现，Results 负责发现，Discussion 负责解释，内部工程规则不争夺正文叙事位置。

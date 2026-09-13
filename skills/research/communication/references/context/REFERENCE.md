# 科研论文写作参考文献

本文件只给 Agent 指定**写作前应实际阅读的已发表论文**。它不是 citation library，不是当前项目的 scientific evidence，也不替代 [`../writing/SCIENTIFIC-WRITING-CONTRACT.md`](../writing/SCIENTIFIC-WRITING-CONTRACT.md)。

不要在本文件复制论文正文、整理“金句”或长期保存大段 excerpt。正式起草长篇 manuscript 前，打开 DOI 对应的正式论文或可核验全文，直接观察作者在真实论文中怎样写 Abstract、Introduction、Methods、Results / 正文主体和 Discussion。

## 1. 每次长篇写作前怎么读

每次开始或重新开始一篇长篇 research article / review 的正文起草时，先读 **3 篇**：

1. 通用结构参考固定读 `10.1371/journal.pcbi.1005619`；
2. 从与当前稿件类型最接近的组中选 2 篇；
3. 生物学与生物信息学真正各占重要贡献时，可以把第 3 篇换成另一学科组的一篇。

局部修 typo、改一个句子、补一个 citation 或执行明确 reviewer comment 时不重复这一流程；开始新稿、重写主要 section、或用户指出当前文字“像 Agent / codebook / 不像论文”时重新执行。

对每篇参考论文，至少实际查看：

- Abstract：背景、目的、方法、headline result、结论分别用了多少文字，作者用什么动词报告贡献；
- Introduction：首段怎样进入领域问题，哪一段建立已有知识，哪一段形成 gap，最后一段怎样声明本文做了什么；
- Methods：科研对象、实验 / 数据、变量、比较、统计或算法怎样被直接命名，哪些细节进入正文、哪些没有；
- Results / 正文主体：每个小节第一段和第一句怎样报告发现或综合判断，数字、Figure / Table 和解释怎样排序；
- Discussion / Conclusion：开头怎样重新陈述主要发现，怎样连接 prior art，limitations 放在哪里，结论怎样控制强度。

只观察这些论文实际使用的**领域术语、句子功能、段落推进和信息密度**。不得复制原句、模仿独特措辞，也不得把参考论文中的 scientific claim 写进当前稿件，除非它已经通过当前项目 Literature 流程成为真实 citation evidence。

如果 DOI 无法访问足以观察正文的全文，不要根据 abstract 猜测整篇写法；换用本组另一篇可访问参考。

## 2. 通用结构参考

### Mensh & Kording, 2017 — PLOS Computational Biology

**Ten simple rules for structuring papers**

DOI: `10.1371/journal.pcbi.1005619`

用途：所有长篇稿件都先看这一篇，重点看 section / paragraph / sentence 怎样围绕读者的信息顺序组织。它是写作结构参考，不是当前稿件的 scientific citation。

## 3. 经验性方法研究 / 元研究 / 文献实践审计

这组适用于“研究对象是既有论文，但本文自己进行了抽样、编码、统计或方法学审计”的 research article。

### Kleine Bardenhorst et al., 2021 — mSystems

**Data Analysis Strategies for Microbiome Studies in Human Populations—a Systematic Review of Current Practice**

DOI: `10.1128/mSystems.01154-20`

### Welsh & Eisenhofer, 2024 — New Phytologist

**The prevalence of controls in phyllosphere microbiome research: a methodological review**

DOI: `10.1111/nph.19573`

写这类稿件时两篇都读。重点直接看它们如何从领域方法学问题进入 empirical gap，怎样写 search / eligibility / extraction / analysis，以及 Results 如何直接报告文献实践分布而不是把正文写成传统技术综述。

## 4. 生物学原始研究

### Kobel et al., 2025 — Nature Communications

**Protozoal populations drive system-wide variation in the rumen microbiome**

DOI: `10.1038/s41467-025-61302-2`

生物学原始研究默认读本篇。重点看 Results subsection 的标题和首句、实验结果怎样推进下一个 biological question、Discussion 如何从主要发现进入 prior art 与机制解释。不要迁移该论文的因果强度到证据更弱的项目。

如果当前稿件以微生物组方法、组学测量或功能解释为核心，再同时读下一组的一篇综述作为术语和解释边界参考。

## 5. 生物学 / 微生物组综述

### Denman, Morgavi & McSweeney, 2018 — Animal

**Review: The application of omics to rumen microbiota function**

DOI: `10.1017/S175173111800229X`

### Djemiel et al., 2022 — GigaScience

**Inferring microbiota functions from taxonomic genes: a review**

DOI: `10.1093/gigascience/giab090`

普通生物学 / 微生物组综述从这两篇中按当前主题选择 2 篇；若当前稿件本身就是 rumen / microbiome 方法综述，两篇都读。重点看作者怎样直接使用领域已有对象组织 section，而不是创造上位抽象框架；同时观察不同 measurement / method 的边界怎样进入正文。

## 6. 生物信息学 / 统计方法 / 软件原始研究

### Love, Huber & Anders, 2014 — Genome Biology

**Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2**

DOI: `10.1186/s13059-014-0550-8`

### Bolyen et al., 2019 — Nature Biotechnology

**Reproducible, interactive, scalable and extensible microbiome data science using QIIME 2**

DOI: `10.1038/s41587-019-0209-9`

写统计方法、算法、生物信息软件、pipeline 或 resource paper 时，从这两篇开始。重点看具体 computational task / failure mode 怎样在 Introduction 中建立，method / software contribution 怎样在 Methods / Results 中被验证，以及 benchmark / application 如何服务贡献而不是取代贡献定义。

## 7. 计算机科学方法论文补充参考

### He et al., 2016 — CVPR

**Deep Residual Learning for Image Recognition**

DOI: `10.1109/CVPR.2016.90`

当生物信息学论文的主要创新确实是 algorithm / model architecture / optimization method，而不是主要作为 biological analysis pipeline 时，再读本篇。重点看 problem → method → controlled comparison → empirical evidence 的论证节奏。计算机科学 benchmark 写法不能替代 biological validation 与 inference boundary。

## 8. 选择规则

默认选择如下：

| 当前稿件 | 写作前实际阅读 |
| --- | --- |
| 生物学原始研究 | `10.1371/journal.pcbi.1005619` + `10.1038/s41467-025-61302-2` + 与当前方法最接近的一篇 |
| 经验性方法研究 / 元研究 | `10.1371/journal.pcbi.1005619` + `10.1128/mSystems.01154-20` + `10.1111/nph.19573` |
| 生物学 / 微生物组综述 | `10.1371/journal.pcbi.1005619` + `10.1017/S175173111800229X` + `10.1093/gigascience/giab090` |
| 生物信息学方法论文 | `10.1371/journal.pcbi.1005619` + `10.1186/s13059-014-0550-8` + `10.1038/s41587-019-0209-9` |
| 算法型生物信息论文 | `10.1371/journal.pcbi.1005619` + `10.1186/s13059-014-0550-8` + `10.1109/CVPR.2016.90` |

如果当前论文与这些参考的文稿类型明显不匹配，不要机械套用；先通过 Literature 找到 1–2 篇更接近的已发表论文，并只在当前稿件中临时作为 writing reference。只有某种写作类型反复出现时，才考虑把新 DOI 加入本文件。

## 9. 阅读后的最低输出

读完参考论文后，不写长篇“文风总结”。只在起草前形成一个短的临时 note：

```text
当前稿件类型：
本次参考 DOI：
Introduction 的真实推进顺序：
Results / 正文主体的小节组织方式：
Discussion 的真实推进顺序：
本领域反复出现的标准术语：
当前稿件最需要避免的内部化表达：
```

这个 note 只用于当前写作 session，不成为新的 scientific authority，也不进入 manuscript。然后再按照当前项目的 scientific evidence 起草正文。

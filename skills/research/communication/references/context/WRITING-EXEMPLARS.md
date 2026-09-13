# 科研写作校准文献

本文件不是 citation library，也不是本项目科学事实来源。它只在需要校准 manuscript **组织方式、段落推进、术语密度、结果呈现和作者语气**时使用。

选择 writing exemplar 时优先取与当前稿件**贡献类型 + 学科 + 文稿类型**最接近的 2–4 篇。学习它们怎样组织问题和证据，不复制句子，不沿用其未被当前项目 evidence 支持的 claim，也不因为 exemplar 的期刊格式而提前绑定当前 venue-neutral manuscript。

## 1. 跨学科结构校准

### Mensh & Kording, 2017 — PLOS Computational Biology

**Ten simple rules for structuring papers**

DOI: `10.1371/journal.pcbi.1005619`

适合校准：

- 一篇论文只保留少量 central contributions；
- 按读者而不是作者的分析过程组织信息；
- paragraph / section / manuscript 都形成 context → content → conclusion 的可读结构；
- topic sentence 让读者提前知道当前段落的任务。

它是结构建议，不是当前研究的 scientific citation。

## 2. 生物学与微生物组综述 / 方法学综述

### Kleine Bardenhorst et al., 2021 — mSystems

**Data Analysis Strategies for Microbiome Studies in Human Populations—a Systematic Review of Current Practice**

DOI: `10.1128/mSystems.01154-20`

适合校准 empirical methodological review：

- Introduction 从已知方法学问题进入“现实文献实践到底怎样”的 empirical gap；
- Methods 直接交代检索、纳入和编码；
- Results 以 research question / practice prevalence 为标题和组织单位；
- Discussion 先总结最重要发现，再解释对领域实践的意义。

### Welsh & Eisenhofer, 2024 — New Phytologist

**The prevalence of controls in phyllosphere microbiome research: a methodological review**

DOI: `10.1111/nph.19573`

适合校准：

- 一个明确的方法学问题如何转化为 literature audit；
- review objective、search / screening、prevalence result 和 practical implication 的直接连接；
- 不需要为 contamination control 再造上位理论体系。

### Denman, Morgavi & McSweeney, 2018 — Animal

**Review: The application of omics to rumen microbiota function**

DOI: `10.1017/S175173111800229X`

适合校准生物学 / rumen omics 综述：

- 直接使用 taxonomic marker genes、metagenomics、metatranscriptomics 等领域对象组织技术讨论；
- 解释每种 measurement 能回答什么 biological question；
- 方法和功能解释围绕 rumen biology，而不是抽象“证据层级”命名。

### Sun et al., 2022 — GigaScience

**Inferring microbiota functions from taxonomic genes: a review**

DOI: `10.1093/gigascience/giab090`

适合校准生物信息 / microbiome 方法综述：

- 从具体任务“由 taxonomic genes 推断 microbiota function”组织全文；
- 比较工具时围绕 input、prediction、validation、适用条件和限制；
- 软件 / database 是解决 task 的手段，不是逐个工具摘要的目录。

## 3. 生物学原始研究

### Kobel et al., 2025 — Nature Communications

**Protozoal populations drive system-wide variation in the rumen microbiome**

DOI: `10.1038/s41467-025-61302-2`

适合校准 rumen / microbiome 原始研究：

- Introduction 从 biological system 与既有知识进入具体 uncertainty；
- Results 标题直接表达 controlled experiment 得到的 biological finding；
- 一个结果自然提出下一个问题，而不是按 omics platform 排列；
- Discussion 从主发现连接历史 prior art、解释和真实设计边界。

这里只学习写作组织。标题中的因果强度不能迁移到证据更弱的项目。

## 4. 生物信息学 / 计算方法原始研究

### Love, Huber & Anders, 2014 — Genome Biology

**Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2**

DOI: `10.1186/s13059-014-0550-8`

适合校准 statistical bioinformatics method paper：

- 第一段先明确 RNA-seq count analysis 这一具体 statistical task；
- 具体说明现有 estimation 在什么条件下困难；
- 方法贡献对应明确的 model components；
- benchmark 和应用用于验证 contribution，而不是用新名词代替性能证据。

### Bolyen et al., 2019 — Nature Biotechnology

**Reproducible, interactive, scalable and extensible microbiome data science using QIIME 2**

DOI: `10.1038/s41587-019-0209-9`

适合校准 software / infrastructure paper：

- 明确现有 workflow 的 reproducibility / extensibility 问题；
- 软件 architecture 与用户可验证能力一一对应；
- resource / software contribution 需要真实 availability 和可重现路径，而不是只展示 biological application。

### He et al., 2016 — CVPR

**Deep Residual Learning for Image Recognition**

适合校准典型计算机科学方法论文：

- 开头立即定义 concrete optimization / representation problem；
- 紧接着说明 proposed method；
- 贡献靠 systematic benchmark 和 comparison 展开；
- Abstract 中 problem → method → empirical evidence 的顺序非常清楚。

它用于学习计算方法的论证节奏，不用于决定生物信息学论文的 biological claim strength。

## 5. 计算研究的评审规范校准

### NeurIPS Paper Checklist

使用 NeurIPS 当前官方 checklist，而不是记忆中的旧版本。适合校准：

- Abstract / Introduction 的 claims 是否准确反映 scope；
- limitations 是否被真实讨论；
- main experimental results 是否有足够 reproduction information；
- baselines 是否也进入复现范围；
- data split、hyperparameter selection、error bars / uncertainty、compute 是否说明。

Checklist 是审查维度，不是文章目录模板；生物信息学论文仍需额外满足 biological design、measurement 与 inference boundary。

## 6. 如何使用 exemplar

不要要求 Agent “模仿某篇论文的文风”。执行下面的校准步骤：

1. 选 2–4 篇最接近当前稿件的 exemplar；
2. 每篇只记录：Abstract 顺序、Introduction gap 路径、section heading 类型、Results / body 的段落任务、Discussion / conclusion 节奏、术语定义位置；
3. 对当前 manuscript 建立自己的 outline；
4. 检查当前稿件是否比 exemplar 更依赖作者自造术语、内部分类或防御性解释；
5. 若存在差异，优先把当前稿件改回具体 scientific object / task / finding，而不是抄 exemplar 句子。

## 7. 增补 exemplar 的条件

只有满足以下条件才向本文件增加长期 exemplar：

- 论文身份可唯一核验（title + venue + DOI / official record）；
- 它代表一种当前 Research family 经常需要的写作类型；
- 能明确说明“学习什么”，而不是因为期刊名气大；
- 新 exemplar 提供现有集合没有覆盖的写作模式。

用户只给出“某期刊某年的一篇 review”而没有足够身份信息时，先核验具体论文；无法唯一确认时不猜测、不写入长期 reference。

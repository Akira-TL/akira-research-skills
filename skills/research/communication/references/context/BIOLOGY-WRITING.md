# 生物学论文写作叠加层

本文件只补充生物学与实验生命科学论文的写作惯例。先遵守 [`SCIENTIFIC-WRITING-CONTRACT.md`](../writing/SCIENTIFIC-WRITING-CONTRACT.md) 的共同生成规则，再根据文稿类型使用原始研究论文或普通综述 workflow。这里不复制通用段落规则，也不规定特定期刊格式。

## 1. 生物学写作首先写“生物学问题”，不是技术清单

生物学论文的主线优先围绕：

```text
生物学对象 / 现象
→ 关键过程或关系
→ 可区分的解释
→ 实验 / 观察证据
→ 当前能够支持的生物学结论
```

测序、显微、组学、培养、模型和统计方法是回答问题的工具。只有当“比较方法本身”就是 Research Question 时，技术路线才成为主叙事对象。

一个结果小节若可以改写成“我们用了 RNA-seq”“我们做了代谢组”“我们又做了蛋白组”，但看不出每一步回答了哪个生物学问题，说明组织单位选错了。

## 2. 原始生物学研究论文

### 2.1 Introduction

Introduction 优先建立：

```text
具体 biological system / phenomenon
→ 已知机制、关系或规律
→ 尚未解决的 biological question / competing explanation
→ 为什么现有 evidence 不能区分它
→ 本研究的实验 / 观察策略和研究问题
```

不要把“使用了更先进的组学平台”本身写成生物学 gap。技术 gap 只有在它直接阻碍目标 biological question 时才进入主线。

### 2.2 Results

生物学 Results 的小标题优先写**观察或结论性发现**，例如：

```text
Treatment X altered rumen fermentation without changing total bacterial load
Gene Y was required for the stress-induced phenotype
Two reproducible community states emerged under the controlled diet intervention
```

标题强度必须服从证据。观察性结果不用 `drives`、`determines`、`is required for` 等因果表达；只有真实干预、遗传扰动、因果识别或相应机制证据允许时才使用。

每个结果小节按以下顺序组织：

```text
本节问题
→ 关键实验 / comparison
→ 直接 observation
→ 必要统计量和 uncertainty
→ control / validation
→ 本节最窄 biological inference
```

Figure / Table 承担数据细节，正文指出决定性 pattern、effect、comparison 和下一步问题。不要逐 panel 朗读，也不要把 Discussion 的机制解释提前塞进 Results。

### 2.3 从 observation 到 mechanism 的证据梯度

写作时明确区分：

- observation：检测到、增加、降低、共现、定位；
- association：变量之间存在统计关联；
- intervention effect：实验处理改变某 endpoint；
- necessity / sufficiency：扰动实验支持“必要 / 足够”；
- mediation：处理效应通过某 mediator 传递，并满足相应识别条件；
- mechanism：多个互补证据直接支持具体过程或因果链。

技术层级不自动等于证据层级。RNA、蛋白、代谢物或多组学更多，并不自动建立 mechanism；实验设计、对照和判别性 evidence 决定结论强度。

### 2.4 Discussion

Discussion 以**生物学发现**组织，而不是按实验技术回顾全文。

每个主题优先：

```text
本研究的 biological finding
→ 与领域已有结果一致 / 不同在哪里
→ 哪些机制或解释与当前 evidence 相容
→ 当前实验实际排除了什么、仍不能区分什么
→ 对该 biological system 的意义
```

机制讨论应引用真正相关的 prior work，并把“plausible explanation”与“demonstrated mechanism”区分开。通用限制集中到 Strengths and limitations；只有直接改变当前解释的边界才留在主题段落。

### 2.5 Methods

Methods 按真实实验顺序和复现需求组织，至少在适用时明确：

- biological material / organism / cohort；
- experimental or observational unit；
- treatment / exposure / comparator / control；
- sampling and randomization / blinding；
- sample collection and processing；
- assay / instrument / reagent / protocol；
- endpoint definition；
- exclusion / missingness / QC；
- statistical model、effect estimate、uncertainty；
- ethics / registration / data and code availability。

同一实验中的技术细节可以详细，但不要把内部项目 validator、文件路径和版本管理写成 scientific method。

## 3. 生物学经验性方法研究 / 元研究

如果研究对象是**文献、报告实践、实验设计或方法使用本身**，但项目产生了新的 sampling frame、coded dataset、prevalence estimate、benchmark corpus 或统计分析，它仍属于原始研究 / empirical methodological study，而不是普通叙述性综述。

这类论文优先采用：

### Introduction

```text
领域中已知的方法学问题
→ 已有 benchmark / review 已经证明什么
→ 现实研究实践中该问题有多普遍仍未知
→ 本研究怎样抽样 / 编码 / 量化
```

### Methods

主文优先交代：

- sampling frame / database / time window；
- eligibility；
- probability / stratified / other sampling design；
- full-text acquisition；
- study-level coding variables 与关键 operational definition；
- estimator、weighting、confidence interval；
- sensitivity analysis；
- 若存在 targeted benchmark corpus，明确它与代表性 sample 的不同 inference role。

完整 codebook、edge cases 和 machine validation 进入 Supplement / repository documentation；正文只保留理解 estimand 和复现 coding 所必需的定义。

### Results

按**经验发现**组织，而不是按 coding taxonomy 组织：

```text
某类设计 / measurement 在代表性样本中有多常见
→ estimate / CI / denominator
→ 关键 subgroup 或 contrast
→ 独立 benchmark 直接证明了什么
```

代表性 probability sample 可以支持预先定义总体的 prevalence inference；non-probability benchmark corpus 只报告其直接比较 evidence，不用其计数估计 field prevalence。

### Discussion

```text
最重要的领域实践分布
→ 与既有 methodological literature 的关系
→ 为什么这些分布影响 biological interpretation / study design
→ benchmark evidence 能支持到哪里
→ sampling / coding / access boundary
```

“不同方法可能影响结果”等成熟常识不作为本文原创贡献；原创性来自对**这些实践在目标文献总体中的真实分布和直接比较证据**进行新的经验量化。

## 4. 生物学普通综述

### 3.1 综述的组织单位

默认优先级：

```text
biological question / process
→ mechanism / pathway
→ phenotype / ecological relation
→ population / system context
→ method（仅当方法差异本身决定结论时）
```

如果目录主要是“16S → metagenomics → transcriptomics → proteomics → metabolomics”，先问 Review Question 是否真的是“比较技术”。若核心问题是某个生物过程或机制，应按 biological question 重组方法证据。

### 3.2 每个主题做跨论文综合

一个主题段落优先写：

```text
当前最稳定的 biological conclusion
→ 支持它的代表性原始研究
→ 冲突 / 条件依赖证据
→ 差异是否来自 species / population / design / measurement / context
→ 当前最窄共识与 unresolved question
```

综述不是按作者顺序缩写摘要。Review / Perspective 可用于建立术语、历史脉络和引用链；决定性生物学 Claim 尽量回到原始研究核验。

### 3.3 Conceptual figure

只有跨论文关系确实已经得到 evidence 支持时，才画机制图或 conceptual framework。图中应能区分：

- 已建立关系；
- 多篇研究支持但存在条件限制的关系；
- 作者综合出的工作模型；
- 尚待检验的 hypothesis。

不要因为综述需要“一个框架图”就把间接关联画成确定机制。

### 3.4 Gap 与 future direction

优先写“哪个 biological question 仍无法回答，以及为什么”。

有效 gap 例如：

- 关键 population / species 尚未测试；
- 现有实验不能区分两个机制；
- measurement 只覆盖 proxy，而目标过程未直接测量；
- 多个研究结论冲突且边界条件未确定；
- 缺少 longitudinal / perturbation / validation evidence。

“研究很少”“尚无系统报道”只有在数量不足确实导致核心问题无法回答时才构成 gap。

## 5. 组学论文的特殊纪律

组学数据容易让 manuscript 被技术名词主导。写作时持续区分：

- taxonomic composition / abundance；
- genomic potential；
- transcription；
- protein abundance；
- metabolite concentration；
- biochemical activity / flux；
- whole-system phenotype。

这些 endpoint 可以互相补充，但不能通过语言直接互换。

对于 microbiome、multi-omics 等论文，优先具体写 measurement 与 biological claim。例如写“RNA abundance increased”或“predicted pathway abundance differed”，而不是创造一个上位“activity evidence layer”来概括全部结果。

## 6. 生物学写作完成检查

成稿至少满足：

- Results 小标题回答 biological question / finding，而不是列技术；
- experimental / observational unit、control 和 endpoint 清楚；
- association、treatment effect、mediation 和 mechanism 没有混用；
- 组学层级没有被写成质量等级；
- Review body 按 biological problem 做 synthesis，而非工具目录；
- Discussion 的主要名词是 organism、cell、gene、pathway、microbe、metabolite、phenotype、environment 等领域对象，而不是项目内部抽象标签。

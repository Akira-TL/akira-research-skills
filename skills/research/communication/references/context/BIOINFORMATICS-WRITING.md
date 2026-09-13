# 生物信息学与计算生物学论文写作叠加层

本文件补充生物信息学、计算生物学、统计基因组学、微生物组计算方法和相关算法 / 软件论文的写作惯例。先遵守 [`SCIENTIFIC-WRITING-CONTRACT.md`](../writing/SCIENTIFIC-WRITING-CONTRACT.md)，再根据整篇文稿是原始研究还是普通综述使用对应 workflow。

生物信息学通常同时面对两个读者群：方法学读者关心 task、assumption、benchmark、runtime、reproducibility；生物学读者关心方法能回答什么 biological question、输出如何解释。论文必须明确每个主要 Claim 的 home discipline，不能用一种证据替另一种证据。

## 1. 先明确 computational contribution 属于哪一种

正式起草前，明确主要贡献：

- algorithm / statistical model；
- computational method / workflow；
- software / infrastructure；
- benchmark / evaluation study；
- database / catalogue / atlas / reusable resource；
- computational biological discovery；
- 上述多项组合。

不同贡献需要不同 evidence。例如新算法必须证明性能和适用范围；软件基础设施必须证明功能、可重现性和实际用途；resource 必须说明构建、覆盖、质量和访问；纯 biological application 不能只靠“用了新模型”替代生物学验证。

## 2. 生物信息学原始研究 / 方法论文

### 2.1 Introduction：task → failure mode → contribution

优先顺序：

```text
具体 computational / biological task
→ 为什么它重要
→ 现有方法在哪个可观察条件下不足
→ 这个不足为什么影响目标分析
→ 本文方法 / resource 做了什么
→ 预先声明的具体 contributions
```

“现有方法不足”应尽量具体，例如：

- dispersion estimation unstable at low counts；
- reference database lacks target taxa；
- current pipeline cannot preserve sample provenance；
- benchmark contains leakage；
- model does not transfer to unseen cohorts；
- runtime / memory prevents target scale。

不要写成空泛的“现有方法存在局限，因此我们提出 X framework”。方法名可以是正式科研产品名称，但其名称本身不是性能证据。

### 2.2 Methods：定义 task 和 comparison contract

Methods 至少在适用时清楚说明：

- input、output 和 prediction / estimation target；
- training / validation / test split；
- preprocessing 与 feature construction；
- model / algorithm / objective function；
- baseline 与 comparator 为什么可比；
- hyperparameter selection；
- simulation / synthetic data generation；
- evaluation metric；
- random seeds / repeated runs / uncertainty；
- software / dependency / hardware / compute；
- data availability、code、version 和 execution instructions。

同一 benchmark 上的比较必须控制 information access。不能让新方法使用 baseline 不可见的 labels、metadata 或 preprocessing advantage，再把差异写成 algorithm superiority。

### 2.3 Results / Evaluation

方法论文的 Results 不只是在 biological dataset 上展示一张好看的 Figure。默认按下列证据层推进：

```text
方法是否实现预期能力
→ controlled / simulated setting 中能否恢复已知 truth 或 target behavior
→ 与合理 baselines 的公平 comparison
→ sensitivity / robustness / failure boundary
→ ablation 或 component analysis（若组件贡献属于 Claim）
→ real biological use case
```

不要求每篇论文机械包含全部层级；只要求每个主要方法 Claim 都有与之匹配的 evaluation。

小标题优先写性能结论或问题，例如：

```text
The model improves low-count dispersion estimates across simulated effect sizes
Performance gains persist across independent cohorts
Database choice dominates species-level classification error for rare taxa
```

而不是“Benchmark 1”“Experiment 2”“Module A”。

### 2.4 Benchmark 结论的强度

严格区分：

- 在一个 dataset 上优于 baseline；
- 在多个预定义 benchmark 上表现稳定；
- 对 distribution shift / external cohort 有 generalization evidence；
- 某 component 与性能变化相关；
- 某 component 解释了模型内部 mechanism；
- biological mechanism。

预测性能提升不能直接证明 biological mechanism。Feature importance、attention、embedding separation、model coefficient 或 post hoc interpretation 也不自动等于 biological causality。

### 2.5 Biological application

如果方法论文包含真实生物学应用，先说明该分析是在：

- 验证方法能否恢复已有 biological signal；
- 发现新的 candidate association；
- 提出新的 biological hypothesis；
- 建立经过独立实验验证的新 biological finding。

前三种不能因为模型复杂而升级成第四种。计算结果若需要实验验证，应把它写成 prediction / candidate / hypothesis，并说明 evidence boundary。

### 2.6 Discussion

Discussion 分开讨论：

1. 方法在什么 task / condition 下真正改善；
2. 与既有方法相比新在哪里；
3. assumptions 和 failure modes；
4. compute / data / reference dependence；
5. biological use case 实际支持到什么；
6. 哪些结果需要 external benchmark 或 experimental validation。

不要把 benchmark 上的有限 improvement 写成“普适解决了 X 问题”。

## 3. 生物信息学普通综述

### 3.1 不按工具名做目录

除非目标本身是 software catalogue，综述不按：

```text
Tool A
Tool B
Tool C
Tool D
```

组织正文。优先按：

```text
task / scientific question
→ input and output
→ modeling assumptions
→ method families
→ evaluation evidence
→ failure modes / applicability
→ unresolved problem
```

例如 microbiome functional inference 综述，应比较不同 input、reference、prediction target、validation evidence 和 applicability，而不是只列软件。

### 3.2 比较方法时先确认“可比性”

跨论文 performance 数字只有在 dataset、split、metric、preprocessing、information access 和 evaluation protocol 足够可比时才能直接排序。

若 benchmark 不可通约，综述应写清：

- 各方法在哪种 task / dataset 上被验证；
- evaluation criterion 有什么不同；
- 哪些 conclusion 可以跨研究综合；
- 哪些只能并列报告。

不要因为某方法更新、更复杂、用了深度学习或更多组学数据，就默认更好。

### 3.3 方法族的综合单位

每个主题优先回答：

```text
这类方法解决什么 task
→ 核心 statistical / computational assumption
→ 已有 benchmark 支持什么优势
→ 在什么条件下失败或退化
→ 对 biological interpretation 有什么影响
→ 当前真正缺什么 evidence
```

方法名称、software table 和 feature checklist 可以辅助比较，但正文要综合“为什么”和“在什么条件下”。

### 3.4 Resource / database / pipeline reviews

若综述对象是 database、reference resource 或 pipeline，至少比较：

- scope / coverage；
- curation / update policy；
- input-output contract；
- version dependence；
- benchmark or validation；
- interoperability / reproducibility；
- known blind spots。

“数据库不同会产生不同结果”不是新的综述结论；需要进一步说明哪些 target、taxa、sample type 或 analysis stage 对这种差异最敏感，以及直接证据到哪里。

## 4. 计算机科学写作习惯如何迁移到生物信息学

可以吸收计算机科学论文的以下习惯：

- Introduction 早期明确 contribution；
- 方法 Claim 与 benchmark 一一对应；
- baselines、ablation、sensitivity、runtime、data split 可核验；
- 结果表直接围绕 task metric；
- code / data / reproduction instructions 清楚。

但不能机械迁移：

- leaderboard improvement 不能替代 biological significance；
- benchmark dataset 不能自动代表真实 population；
- statistical significance、predictive accuracy 与 causal / mechanistic evidence 属于不同问题；
- 计算方法的“interpretability”不能自动当作生物机制解释。

## 5. 生物信息学写作完成检查

成稿至少满足：

- 读者能用一句话说出 task、input、output 和 main contribution；
- 每个方法 Claim 都能指出对应 benchmark / analysis；
- baseline comparison 公平且可复现；
- dataset split / leakage / hyperparameter policy 交代清楚；
- 方法性能与 biological claim 分开论证；
- Review body 按 task / assumption / evidence / applicability 综合，而非工具清单；
- 复杂模型、更多参数和更新技术没有被当成质量等级；
- 新方法名称之外，没有为了“理论感”再造一套解释 benchmark 的内部术语。

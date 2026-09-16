# Scientific Assessment

以 Claim 为单位，而不是以 section checklist 为单位审查科学有效性。

## Claim chain

对每个 central / load-bearing Claim 依次回答：

1. **Claim**：稿件实际声称什么，inference level 是描述、关联、因果、机制还是过程；
2. **Evidence**：哪些 Experiment / Study / Dataset / Analysis / Figure / Table 直接承担这个 Claim；
3. **Necessary assumptions**：从 evidence 到 Claim 需要哪些识别、measurement、model、independence、missingness、transportability 或其他前提；
4. **Alternative explanations**：哪些解释仍与当前 evidence 兼容；
5. **Supported inference**：在当前 Design 与 Analysis 下，最强仍诚实成立的结论是什么。

## 适用维度

根据 Claim 实际需要选择检查，不做固定配额：

- Research Question / estimand / outcome alignment；
- sampling、comparison、control、confounding、selection 与 internal validity；
- measurement validity、assay / instrument / label / proxy boundary；
- statistical / computational model、uncertainty、multiplicity、sensitivity、robustness；
- causal identification 与 mechanistic evidence；
- temporal / process inference；
- external validity、population / system / condition scope；
- reproducibility 与足以复核主要结果的报告完整性。

一个维度只有在其失败会改变 Claim truth、scope、uncertainty 或主要 interpretation 时，才构成实质科学问题。

## 科学后果优先

不要只写“方法没有说明”或“建议增加分析”。先说明该缺口对科学判断造成什么后果，例如：

- 无法区分目标效应与 confounding；
- 当前 analysis 只识别 association，不能支持 causal Claim；
- measurement 只能支持 proxy-level Claim；
- uncertainty 未量化到足以判断 central contrast；
- 结果只在当前 sample / system 内成立，外推范围过宽。

Reviewer 的任务是把 evidence boundary 显式化，而不是替作者设计一个更大的研究。

# Review → Research Handoff

Review Result 的终点是学术判断、Concern、resolution criterion 与必要的 hand-back route。Reviewer 不直接修改作者侧 canonical scientific state。

## 1. 先交付 Review Result

对需要后续工作的 Concern，至少返回：

- Target Claim / section；
- 当前 assessment 与 scientific consequence；
- resolution criterion；
- minimum honest remedy；
- stronger evidence option（若适用）；
- 建议的 Research hand-back route。

这一步只说明“要解决该 Concern 需要哪类工作”，不等于已经授权修改项目。

## 2. 用户决定后才进入 Research

只有用户明确决定处理 Review Result 后，才把相应工作交回 `akira-research`。用户可以采纳、部分采纳、拒绝、延期或要求进一步讨论；Reviewer 不替用户自动扩大研究范围。

按真实工作类型路由：

- 缺少外部 evidence / prior work → `akira-research → literature`；
- 需要新统计、计算、robustness / sensitivity → `akira-research → analysis`；
- 需要重新界定 Observation → Claim、causal / mechanistic / scope 边界 → `akira-research → interpretation`；
- 需要新的 estimand、sampling、control、measurement 或 protocol → `akira-research → design`；
- 需要真实新实验 / 采样 / assay execution → `akira-research → study`；
- 需要 Dataset identity、QC、curation 或 freeze → `akira-research → data`；
- 科学状态已经足够，只需要稿件表达、response letter、Figure 或 submission package 修改 → `akira-research → communication`。

若一个 Concern 同时涉及多类工作，由 `akira-research` 基于新的 scientific state 决定实际顺序，不由 Reviewer 固定 Research Current Loop。

## 3. Reviewer 的写权限边界

未经用户决定，Review 不修改：

- `RESEARCH.md`；
- `.research/research.sqlite` 或其他 Research database；
- canonical Claim / Interpretation；
- manuscript 或 Communication Product；
- Design / Study / Dataset / Analysis canonical artifact。

Review 过程中为了评议而取得的外部文献、临时比较或 reviewer notes 也不自动进入项目 canonical Literature state。

## 4. 修订后可重新进入 Review

Research / Communication 完成用户批准的修改后，可以把新的 manuscript / evidence 作为新 Review Packet 再次交给 `akira-review`。若目标是判断原 Concern 是否闭合，路由到 `review-revision`；新一轮 Review 仍重新确认信息边界，不继承未经授权的作者内部状态。

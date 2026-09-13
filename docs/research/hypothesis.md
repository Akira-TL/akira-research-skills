# hypothesis

`hypothesis` 在存在真正竞争性解释时，把科学猜想组织成可检验的 Hypothesis、Prediction、Discriminator 和结果前判别边界。

Hypothesis 是可选科研对象。描述性、探索性或公开数据研究如果没有真实竞争解释，不会为了流程完整度被强制建立 Hypothesis。正式 Hypothesis 会在结果可见前冻结，并保留其来源与后续 Evaluation 历史。

长期人类 Hypothesis Set 固定写入 `hypotheses/<slug>.md`，目录索引为 `hypotheses/README.md`。正文使用固定 H1/H2 与 Navigation，具体假设、预测和判别细节在 H3+ 展开。目录索引固定包含 `Objects` 与 `Relations`：前者列出 Hypothesis Set，后者链接数据库中已知的相关 Design 等对象，以承担冻结正文之外的反向发现。首次进入 frozen 前，`research-db` 会先机械核验固定路径、章节顺序和已知上游导航，再执行学术语言检查；检查失败不会写入 frozen 状态。冻结后不为了后来出现的 Design/Analysis 回写正文，下游反向发现由可更新索引与 Research Tree 承担。

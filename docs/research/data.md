# data

`data` 管理从 raw 到 curated、derived 和 analysis-ready 的 Dataset 身份、metadata、QC、sample mapping、artifact provenance 与 freeze 边界。

Dataset 表示进入数据管理的对象，不替代产生这些数据的 Study，也不替代后续 Analysis。大型数据可以保存在外部位置，但其稳定 identity、版本、来源和与 Analysis 的时序关系必须可追溯。

高通量测序（Next-Generation Sequencing, NGS）数据需要 BCL/FASTQ 处理、read QC、alignment、quantification、variant/peak/taxonomy calling、reference/database 或其他 assay-specific pipeline 时，由 `data` 调用 `ngs` 执行；NGS runner 负责计算事实，Dataset identity、sample mapping、QC/exclusion timing、raw/curated/derived 与 freeze 仍由 `data` 决定。

长期人类 Dataset 入口固定为 `data/<slug>/README.md`，目录索引为 `data/README.md`。正文使用固定 H1/H2 与 Navigation；来自本项目 Study 时必须链接该 Study，外部 Dataset 则明确真实来源而不制造 Study 链接。目录索引固定包含 `Objects` 与 `Relations`，后者用相对链接展示已知来源 Study 与消费该数据的 Analysis。

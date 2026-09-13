# ngs

`ngs` 是 Akira Research 的高通量测序（Next-Generation Sequencing, NGS）领域执行层。它不新增科研阶段，而是在 `data` 和 `analysis` 需要处理 BCL、FASTQ、BAM/CRAM、VCF、表达矩阵、峰集、ASV/分类谱等测序对象时提供 assay-specific 的流程、资源检查、runner 和 execution provenance。

## 分层

- 真实样本处理、建库、测序仪运行和偏差仍由 `study` 记录。
- BCL → FASTQ、QC、alignment、quantification、variant/peak/taxonomy calling 等主要形成 derived Dataset 的工作由 `data → ngs` 执行。
- differential expression/accessibility/binding/abundance、clustering、enrichment、sensitivity 等回答统计问题的工作由 `analysis → ngs` 执行。
- 生物学解释、因果或机制 Claim 仍交给 `interpretation`。

## Upstream

Akira 不复制第三方 NGS Skill 正文。`ngs-analysis` 是按需外部执行来源，不是安装 Research family 的前置依赖；Lattice 环境可以继续提供 `~/.agents/external/ngs-analysis` 固定 source view，独立科研项目也可以使用用户明确安装或提供的等价官方来源。真正进入 NGS execution 而 upstream 缺失时，Agent 只报告所需能力并请求用户决定，不自行安装或猜测 runner 参数。

upstream 的自动方法选择、软件 fallback 和方便性默认不拥有科研决策权。确认性分析的方法、design formula、contrast、normalization、covariate、multiple-testing 与 sensitivity 必须先由 Akira `analysis` 依据 Research Design 和 estimand 决定，再交给 NGS runner 执行。

## Provenance

OpenAI run envelope 保存具体计算事实；Akira `research.sqlite` 保存它属于哪个 Dataset / Analysis、对应什么 Research Question、何时冻结以及能支持到什么科学边界。每次真实执行还记录 upstream Git commit、plugin version 和 runner/workflow 路径；确认性 Analysis 必须在结果生成前固定这些 source pointers。一个 upstream runner 同时产生 Dataset transformation、QC、clustering 或 inferential result 时，Akira 仍按 `data` / `analysis` 的对象语义分别登记。upstream 自己的 checksum 可以保留在 run-local artifact index 中，但不会变成 Akira 对所有科研 artifact 的普遍 checksum 要求。

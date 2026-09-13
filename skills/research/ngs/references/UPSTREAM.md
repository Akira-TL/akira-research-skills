# OpenAI NGS upstream 边界

## Source of truth

`ngs` 是 Akira Research 的可选领域适配层；OpenAI `ngs-analysis` 仍是独立第三方执行来源，不随本仓库 vendoring，也不是安装 Research family 的前置条件。

任务真正进入 NGS execution 时，先检查当前项目是否已经提供可核验的 OpenAI NGS Skill / runner。若没有，使用 Akira Router 登记的 OpenAI Plugins 来源查看当前 Skill 清单，并只定位与 assay 直接相关的最窄候选。

**不存在可核验 upstream 时只把 NGS execution 标为 optional dependency blocker**：说明需要的 assay / runner 与来源，然后先检查机器级 `~/.agents/skills/`，缺失时请求用户决定是否安装所需 Skill；不得扫描任意路径、循环尝试安装、从模型记忆重建 runner 参数，或把第三方正文复制进 Research repo。具体执行器如何加载机器级 Skill 由执行器自己负责。

使用用户批准的 upstream 后，记录实际来源、版本 / commit、安装位置与 runner/workflow identity。旧首次接入曾使用 OpenAI `plugins` 中的 `ngs-analysis` 1.0.3；这只是历史基线，不代表当前项目必须使用该版本。

## Upstream lane map

当前 upstream 提供相应路径时，根据实际任务按需读取最窄 Skill，例如：

```text
skills/ngs-analysis-router/SKILL.md
skills/ngs-runtime-env/SKILL.md
skills/ngs-bcl-to-fastq/SKILL.md
skills/ngs-fastq-qc/SKILL.md
skills/ngs-bulk-rnaseq/SKILL.md
skills/ngs-bulk-rnaseq-counts-qc/SKILL.md
skills/ngs-bulk-rnaseq-differential-expression/SKILL.md
skills/ngs-scrna-seq/SKILL.md
skills/scrna-seq-qc/SKILL.md
skills/ngs-dna-variant-calling/SKILL.md
skills/ngs-dna-germline-variants/SKILL.md
skills/ngs-dna-somatic-variants/SKILL.md
skills/ngs-dna-umi-panel-variants/SKILL.md
skills/ngs-epigenomics-peaks/SKILL.md
skills/ngs-atacseq-peaks-qc/SKILL.md
skills/ngs-chip-cutrun-peaks-qc/SKILL.md
skills/ngs-amplicon-microbiome/SKILL.md
skills/ngs-shotgun-metagenomics/SKILL.md
```

通用 registry / run-envelope 等资料也只从当前实际 upstream 读取。调用 runner 前读取其当前 `--help` 或源码参数定义，不从旧会话、本文件或模型记忆缓存具体 CLI 参数。

## Akira 覆盖规则

upstream 提供 execution implementation 与 assay-specific guidance，但以下决定仍由本仓库 canonical Skill 拥有：

- Research Question、Active Uncertainty 与 branch：`akira-research` / `research-tree`；
- Study / Sample / Assay 的真实发生事件：`study`；
- Dataset identity、sample mapping、QC/exclusion timing、raw/curated/derived、freeze：`data`；
- estimand、design formula、contrast、统计方法、confirmatory/exploratory、sensitivity：`analysis`；
- scientific Claim 与 evidence boundary：`interpretation`；
- 适用科研规范：`research-standards`。

当 upstream guidance 与上述科研语义冲突时，保留 upstream 作为工具实现依据，并按 Akira scientific contract 决定是否执行、如何解释以及需要什么 amendment。

## 安装与下载

upstream 的 preflight / install plan 可以用于确定缺失工具，但实际安装、较大 reference/database 下载、专有许可、账户认证、cloud execution 或受控数据上传必须遵守当前项目与用户授权。不要因为 upstream runner 支持某条路径就推定当前项目有权限使用。

# Akira Research Skills

Akira 的完整科研 Agent Skills 产品仓库。它从原 `Akira-TL/skills` 的 Research family 抽离并保留相关 Git 历史，使科研项目可以只安装科研能力，而不同时安装知识管理、工程或其他 Akira 产品族。

## 包含的 Skills

```text
akira-research       科研总 Router 与项目状态 / research.sqlite
research-tree        Research Question、Active Uncertainty 与科研分支
research-standards   当前适用科研规范与权威来源核验
literature           文献发现、深读、Critical Audit、综合与长期监测
literature-access    正文 / Supplement / artifact 获取与验收
hypothesis           competing hypotheses 与结果前 prediction
design               estimand、sampling、measurement、controls 与 protocol
study                真实研究实施、Sample / Assay / deviation provenance
data                  Dataset identity、QC、curation、freeze
analysis              统计 / 生信 / 机器学习分析与 Analysis Attempt
interpretation        Observation → Claim、Hypothesis 更新与 evidence boundary
communication         论文、综述、Proposal、Figure、revision 与 submission
ngs                   可选的 NGS 领域执行适配层
```

这些 Skill 共享同一套 Research Tree、`RESEARCH.md`、`research.sqlite` 和 Git provenance；它们作为一个产品族一起版本化，避免跨仓拆散 schema、migration 与科研对象语义。

## 安装

上传到 GitHub 后，科研项目可以直接项目级安装整个产品族：

```bash
npx skills add Akira-TL/akira-research-skills --skill '*' --agent '*' -y
```

本地开发可直接使用 checkout：

```bash
npx skills add . --list
npx skills add . --skill '*' --agent '*' -y
```

不加 `-g` 时由 `skills` CLI 安装到当前项目。项目只需要科研能力时无需安装 Akira 的其他产品仓库。

## 外部能力

Research family 自己拥有科研决策、evidence boundary 与 provenance。浏览器控制、DOCX/PPT 等通用生产力能力，以及 PyMC、RDKit、NGS runner 等专业工具能力均视为可选执行依赖；只有当前任务真实需要且本项目缺少时才按契约提示用户安装或提供。

`ngs` 是适配层，本仓库不会 vendoring OpenAI `ngs-analysis` 正文。若任务实际进入 NGS execution，而对应 upstream source / runner 尚不可用，Agent 必须明确报告并请求最窄外部能力，不得把缺失 runner 当成本仓库安装失败，也不得自行猜测第三方 CLI。

## 目录

```text
docs/
  research/             面向使用者的 Research Skill 文档
skills/
  research/             稳定 Research Skills
    akira-research/     research DB、migration、tests、总 Router
    literature/
    analysis/
    ...
  in-progress/          尚未稳定的 Research Skills
  deprecated/           已弃用 Skill 的迁移说明
AGENTS.md               本仓库维护规则
```

## 历史

本仓库由原 `Akira-TL/skills` 中的 `research/` 与 `docs/research/` 通过 history filtering 抽取，并保留 Research workflow 的主要演进历史。独立仓建立后，稳定 Skill 采用与 Matt 仓一致的 category 结构：`skills/research/` 与 `docs/research/` 镜像维护。

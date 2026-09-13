# Akira Research Skills

Akira Research 是完整的科研 Agent Skills 产品仓。它围绕 Research Question、证据、Research Tree、研究设计、真实实施、数据、分析、解释与科学传播工作，而不是把科研压成固定线性步骤。

## Workflow

```text
Research Question / Active Uncertainty
→ Research Tree
→ Literature / Hypothesis / Design
→ Study / Data / Analysis
→ Interpretation
→ Communication
```

`akira-research` 是顶层 Router，根据当前 scientific state 选择下一条真实工作。

## Skills

稳定 Skill 位于 [`skills/research/`](skills/research/README.md)，包括 `akira-research`、`research-tree`、`research-standards`、`literature`、`literature-access`、`hypothesis`、`design`、`study`、`data`、`analysis`、`interpretation`、`communication` 与 `ngs`。

## Project state

科研项目使用 `RESEARCH.md` 保存当前状态，`.research/research.sqlite` 保存结构化 provenance，Git 固定代码与文档版本，论文、Dataset、分析结果和 Figure 等继续作为独立 canonical artifacts 保存。

## Installation

```bash
npx skills add Akira-TL/akira-research-skills --skill '*' --agent '*' -y
```

查看可安装 Skill：

```bash
npx skills add Akira-TL/akira-research-skills --list
```

本地维护 checkout 使用 `npx skills add . --list`。安装约定见 [`.agents/install-block.md`](.agents/install-block.md)。

## Optional capabilities

浏览器、DOCX/PPT、软件工程方法和第三方专业执行能力不随 Research suite 自动安装。只有当前科研任务真实需要时才补充，它们也不能替代本仓对科研状态和证据边界的管理。

## Repository layout

```text
akira-research-skills/
├── .agents/                 # invocation、文档约定与 ADR
├── docs/research/           # 人类可读 Skill 文档
├── scripts/                 # 仓库检查入口
├── skills/
│   ├── research/            # 稳定 Research Skills
│   ├── in-progress/         # 尚未稳定
│   └── deprecated/          # 弃用与迁移说明
├── AGENTS.md
├── CONTEXT.md
├── CHANGELOG.md
└── README.md
```

## Development

```bash
./scripts/list-skills.sh
./scripts/check.sh
```

修改稳定 Skill 时同步 `docs/research/<skill-name>.md`。调用边界见 [`.agents/invocation.md`](.agents/invocation.md)。

## History

本仓由原 `Akira-TL/skills` 的 Research family 通过 history filtering 抽取，主要科研工作流演进仍可在 Git history 中追溯。独立后采用 category / lifecycle / docs mirror 结构维护。

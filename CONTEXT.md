# Repository context

## Purpose

`akira-research-skills` 是 Akira 的独立科研 Skill 产品仓。它维护从研究问题、文献证据、研究设计、实验实施、数据、分析、解释到科学传播的统一科研工作流。

## Ubiquitous language

**Research Tree**：项目的科研问题、竞争路线与当前活动分支，不等同于任务清单。

**Active Uncertainty**：当前最需要被证据区分的科学不确定性。

**Canonical scientific state**：由 `RESEARCH.md`、`.research/research.sqlite`、Git 与 canonical artifacts 共同构成的可核验科研状态。

**Dataset**：具有稳定身份、来源、处理状态和 freeze 边界的数据对象。

**Analysis**：围绕明确科研问题、estimand 或 exploratory objective 的分析对象。

**Attempt**：同一 Analysis 下的一次可重建执行或方法尝试。

**Observation**：直接由数据或分析产物支持的描述性结果。

**Claim**：经过 Interpretation 后、带有证据强度和适用边界的科学判断。

**Human literature note**：给人阅读的论文 Markdown；与机器 artifact、Agent 阅读状态和用户阅读确认分离。

## Repository boundary

稳定 Skill 位于 `skills/research/`，用户文档位于 `docs/research/`。`akira-research` 是顶层 Router；其他 Skill 负责各自科研对象和执行阶段。

通用浏览器、DOCX/PPT、软件工程方法和第三方专业执行能力不是本仓正文。它们只有在真实任务需要时才作为外部能力接入，不能反向改变 Research 的科研状态和证据边界。

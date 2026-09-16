# Repository context

## Purpose

`akira-research-skills` 是 Akira 的独立科研 Skill 产品仓。它同时维护研究者 / 作者侧的 Research series 与学术评议者侧的 Review series：前者覆盖从研究问题、文献证据、研究设计、实验实施、数据、分析、解释到科学传播的统一科研工作流；后者基于明确评议材料边界审查研究主张、证据与科学推断。

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

**Review Packet**：一次 Review 被明确允许读取的材料集合；independent review 不因与 Research project 同仓而自动包含作者内部 canonical scientific state。

**Assessment Boundary**：一次学术评议实际可见的材料、缺失材料、可判断维度与 Not Assessable 维度；它限定 Reviewer 能够诚实作出的判断。

**Concern**：Reviewer 对具体 Claim / section / evidence 的可定位学术问题，带有科学后果、严重度、confidence 与 resolution criterion。

**Review Result**：Review 输出的学术判断、Concern、resolution criterion 与建议 hand-back route；它本身不修改 Research canonical scientific state 或 manuscript，是否采纳由用户决定。

## Repository boundary

稳定 Skill 位于 `skills/research/`，用户文档位于 `docs/research/`。`akira-research` 与 `akira-review` 是平级的顶层 Router：前者拥有 Research series 与 canonical scientific state，后者拥有 Review series 的评议入口与判断组织；其他 Skill 负责各自科研对象和执行阶段。

通用浏览器、DOCX/PPT、软件工程方法和第三方专业执行能力不是本仓正文。它们只有在真实任务需要时才作为外部能力接入，不能反向改变 Research 的科研状态和证据边界。

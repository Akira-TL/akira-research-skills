# Issue tracker: GitHub

本仓库的 Spec、Ticket 和工程工作项使用 GitHub Issues。所有 tracker 操作统一使用 `gh`。

## Repository

当前仓库：`Akira-TL/akira-research-skills`。

GitHub repository identity 仍以当前 Git remote 为事实来源，不在工程流程中复制第二份 remote 配置。

## Pull requests as a triage surface

**PRs as a request surface: no.**

## Publishing

当 Skill 要求 “publish to the issue tracker” 时，创建 GitHub Issue。

`to-spec` 创建 canonical Spec issue；Spec 本身不加 `ready-for-agent`。

`to-tickets` 从 Spec 创建可执行 Ticket，并使用 `ready-for-agent` workflow role。

## Workflow roles

实际 GitHub label 必须从 `docs/agents/triage-labels.md` 读取。不得假定 canonical role 名永远与 tracker label 相同。

## Dependencies and sub-issues

GitHub 原生 issue dependency 与 sub-issue relationship 是首选表示。

在使用 `gh` convenience flags 前先检查当前安装的 `gh` 是否实际支持；不根据版本号或在线文档猜测。若 CLI 不暴露相应参数但 GitHub API 支持，则使用已经认证的 `gh api`。只有 GitHub dependency / sub-issue API 本身不可用时，才退化到 issue body 中的机器可读关系。

## Claim and completion

可执行 Ticket 的 tracker-visible claim 使用 assignee。若多个 Agent 共用同一个 GitHub identity，则具体 coordination workflow 可以使用更强的 deterministic claim；assignee 只作为可见状态。

完成 Ticket 前必须重新核验 Acceptance Criteria，只勾选真实建立的项目。存在未满足 criterion 时保持 Issue open。完成普通 Ticket 不得顺带关闭其父 Spec。

## Wayfinder

Wayfinder Map 使用 `wayfinder:map`。

子决策票根据类型使用：

- `wayfinder:research`
- `wayfinder:prototype`
- `wayfinder:grilling`
- `wayfinder:task`

Map、sub-issue、dependency 与 frontier 查询均优先使用 GitHub 原生关系；缺失 convenience flag 时使用 `gh api`，不因为本机 CLI 较旧而要求升级。

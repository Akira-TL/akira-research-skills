# Workflow Role Mapping

本文件把当前安装的 Matt 工程流程使用的 workflow role 映射到本仓库的 GitHub labels。

| Workflow role | GitHub label | Used by | Meaning |
| --- | --- | --- | --- |
| `ready-for-agent` | `ready-for-agent` | `to-tickets`, `triage` | 已完整规格化，可由 Agent 执行 |
| `bug` | `bug` | `triage` | 缺陷 |
| `enhancement` | `enhancement` | `triage` | 功能或改进 |
| `needs-triage` | `needs-triage` | `triage` | 尚待维护者分类与判断 |
| `needs-info` | `needs-info` | `triage` | 等待报告者补充信息 |
| `ready-for-human` | `ready-for-human` | `triage` | 需要人工实现或判断 |
| `wontfix` | `wontfix` | `triage` | 当前不处理 |
| `wayfinder:map` | `wayfinder:map` | `wayfinder` | Wayfinder Map |
| `wayfinder:research` | `wayfinder:research` | `wayfinder` | 外部研究型决策票 |
| `wayfinder:prototype` | `wayfinder:prototype` | `wayfinder` | 原型验证型决策票 |
| `wayfinder:grilling` | `wayfinder:grilling` | `wayfinder` | 需要人与 Agent 讨论决定的票 |
| `wayfinder:task` | `wayfinder:task` | `wayfinder` | 为解除决策阻塞而执行的任务 |

下游 Skill 使用 workflow role 表达语义，再通过本文件取得实际 tracker label；即使当前两者同名，也不得绕过这一映射约定。

Setup 只创建缺失 label，不修改已有 label 的颜色或描述。

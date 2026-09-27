# 外部科研 Skill 按需使用规则

Akira Research 的科研决策、Research Tree、provenance、evidence boundary 和完成门禁始终由 Akira 自己的 canonical Skill 管理。第三方 Skill 只能补充具体软件、数据库、领域工具或执行知识，不能成为第二个科研 Router。

## 1. 默认不安装

外部 Skill 不由 Lattice 根安装器预装；只有真实任务需要时，Research 才把能力缺口交给 `akira` Router，由它通过 Skiloom 完成 discovery、Candidate plan 与用户授权后的生命周期动作。外部 Skill 也不以 Git submodule 的方式挂入 Akira 自研 Skill 源码。

当前允许作为按需发现源的科研 Skill 仓库为：

```text
K-Dense-AI/scientific-agent-skills
```

“允许发现”只表示可以检查候选，不表示仓库内任何 Package 已预先通过 Skiloom admission、安装授权或执行授权。

## 2. 什么时候才推荐外部 Skill

只有同时满足以下条件时才向用户提出安装建议：

1. 当前已经有明确科研任务，不是为了扩充能力而浏览 Skill；
2. Akira 自身规则已经确定“为什么要做”，缺的是具体专业工具、数据库或软件实现知识；
3. 当前会话没有已经可用且足够的同类 Skill；
4. Skiloom 当前 Target 也没有满足该能力的 accepted Package；
5. 候选第三方 Skill 能显著降低 API / 软件误用、领域实现错误或重复查文档成本；
6. 安装可以收敛为所需的具体入口 Package，而不是整仓预装。

例如：Analysis 已根据科研问题决定需要 PyMC 实现层级模型，此时可以推荐 PyMC 专门 Skill；不能因为发现 PyMC Skill 就反过来决定科研问题应该使用贝叶斯模型。

## 3. 推荐前必须核验

在向用户请求安装许可前，至少核验并展示：

- 来源仓库与候选 Package / Skill identity；
- Candidate plan 的 exact source revision 与 dependency graph；
- 该 Skill 自己适用的 license；
- 是否包含脚本、hook、安装器或会执行任意代码的指令；
- 是否要求联网、API key、账户、专有服务、cloud execution 或额外 package 安装；
- 是否会读取或上传项目数据；
- 与现有 Akira / accepted Package 是否职责重叠；
- 为什么当前任务确实需要它，以及不安装时的替代路径。

带脚本、hook、网络调用、凭据或数据上传能力的 Skill 不能只凭仓库 allowlist 自动获得执行许可。

## 4. 生命周期只通过 Skiloom

发现候选优先使用 `skiloom-discover` / `skiloom search`。用户选定候选后，由 `akira` Router 把它收敛为明确 Package coordinate 与 source mode，并先运行 Candidate plan。

对于明确的 GitHub source，可采用：

```text
skiloom install <owner>/<repo>/<package> --git <ref> --scope user --plan --json
```

只有 Package admission、source resolution 与 Candidate Graph 都成立，且用户明确授权后，才提交：

```text
skiloom install <owner>/<repo>/<package> --git <ref> --scope user --yes --json
```

不得整仓预装，也不得因为来源已登记就绕过用户决定。若 upstream 不能通过 Skiloom admission，保持 blocker；Research 和 `akira` 都不得调用历史 Git + symlink installer 绕过标准。

Skiloom Registry / accepted state 记录的是 Package 生命周期事实，不替代科研 provenance。第三方 Skill 本身不是科研事实源；如果它实际影响 Analysis / Study，真正的科研 provenance 仍记录具体软件、方法、参数、数据和执行版本，而不是只记录“用了某个 Skill”。

## 5. 用户拒绝安装时

用户拒绝外部 Skill 默认不构成科研 blocker。Agent 应优先改用：

- 已有能力；
- 软件官方 documentation / vignette / `--help`；
- 当前主模型直接实现；
- 其他不需要新增 Skill 的可审计方案。

只有当当前任务确实无法在缺少该外部能力的情况下继续，才按普通科研 blocker 规则说明具体缺失条件。

## 6. 权限边界

外部 Skill 可以负责：

```text
某软件 API 如何正确调用
某数据库如何查询
某领域工具的输入输出与常见陷阱
某成熟 package 的实现细节
```

外部 Skill 不拥有：

```text
Research Question
Hypothesis
Design
Study / Dataset identity
estimand / target contrast
confirmatory / exploratory 决策
Research Tree
Git 科研 provenance
scientific Claim / evidence boundary
Communication 写作类型路由
```

若外部 Skill 的建议与 Akira scientific contract 冲突，先保留其工具层信息，再由 Akira 决定是否执行、如何 amendment 以及结果能支持到哪里。

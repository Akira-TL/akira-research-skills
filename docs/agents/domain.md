# Domain Docs

Matt 工程流程在探索和规划本仓库修改前，应先读取与当前任务相关的领域文档和架构决定。

## Domain context

本仓库采用 single-context：

- 根目录 `CONTEXT.md` 是仓库级领域词汇、科研对象与产品边界的 canonical context。
- 不使用 `CONTEXT-MAP.md`。
- 输出 Spec、Ticket、ADR、测试名称和架构说明时，应沿用 `CONTEXT.md` 已定义的术语，不为同一概念自行创造同义名称。

如果某个必要概念尚未定义，应先判断它是真实领域缺口还是 Agent 自己创造的新术语；不能静默引入新的领域词汇。

## ADR convention

本仓库已有长期架构决定约定：`.agents/adr/NNNN-slug.md`。

继续保留这一约定，不建立平行的 `docs/adr/`。

开始涉及既有产品边界、Skill ownership、Router、状态模型、安装关系或其他长期架构决定的工作前，应读取相关 ADR。

若新方案与既有 ADR 冲突，应显式指出冲突并决定是否修订或取代原决定，不能静默覆盖。

## Missing documentation

某个 domain document 当前不存在时，可以继续当前工作，不为了满足目录形式提前创建空文档。只有在真实领域概念或长期架构决定需要持久化时再补充相应文档。

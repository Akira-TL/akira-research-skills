# Research Skill 调用边界

本仓所有稳定 Skill 位于 `skills/research/<name>/`。调用边界只有两类：

- **User-invoked**：只能由用户明确启动。`SKILL.md` 设置 `disable-model-invocation: true`，同目录 `agents/openai.yaml` 设置 `policy.allow_implicit_invocation: false`。
- **Model-invoked**：模型和用户都可以调用。`SKILL.md` 不设置 `disable-model-invocation`，`agents/openai.yaml` 也不添加禁止隐式调用的 policy。

本产品族有两个顶层 user-invoked Router：

- `akira-research`：Research series 的研究者 / 作者侧 Router，拥有 canonical scientific state 与科研执行路由；
- `akira-review`：Review series 的学术评议 Router，负责基于当前评议材料形成独立的科学判断与 Concern。

其余稳定 Skill 默认 model-invoked，由所属 Router 或相邻科研 Skill 按当前任务调用。Research series 的共享状态以 `RESEARCH.md`、`.research/research.sqlite`、Git 与 canonical artifacts 为事实来源；Review series 不因同仓而自动获得这些作者内部状态的读取权，其输入边界由 `akira-review` 明确固定。

Skill 之间用名称和科研对象契约协作，不通过跨 Skill 相对路径复制对方规则。

新增或改变 Skill 调用方式时，同时更新：

1. `SKILL.md` frontmatter；
2. `agents/openai.yaml`；
3. `skills/research/README.md`；
4. `docs/research/<name>.md`；
5. 若影响顶层路由，再更新 `akira-research`。

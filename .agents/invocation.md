# Research Skill 调用边界

本仓所有稳定 Skill 位于 `skills/research/<name>/`。调用边界只有两类：

- **User-invoked**：只能由用户明确启动。`SKILL.md` 设置 `disable-model-invocation: true`，同目录 `agents/openai.yaml` 设置 `policy.allow_implicit_invocation: false`。
- **Model-invoked**：模型和用户都可以调用。`SKILL.md` 不设置 `disable-model-invocation`，`agents/openai.yaml` 也不添加禁止隐式调用的 policy。

`akira-research` 是本产品族唯一的顶层 user-invoked Router。其余稳定 Research Skill 默认 model-invoked，由 `akira-research` 或相邻科研 Skill 按科学状态调用。

Skill 之间用名称和科研对象契约协作，不通过跨 Skill 相对路径复制对方规则。共享状态以 `RESEARCH.md`、`.research/research.sqlite`、Git 与 canonical artifacts 为事实来源。

新增或改变 Skill 调用方式时，同时更新：

1. `SKILL.md` frontmatter；
2. `agents/openai.yaml`；
3. `skills/research/README.md`；
4. `docs/research/<name>.md`；
5. 若影响顶层路由，再更新 `akira-research`。

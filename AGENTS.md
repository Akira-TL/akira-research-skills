# Repository instructions

本仓库是 Akira Research Skills 的 canonical source。它只维护完整科研产品族：科研总 Router、Research Tree、科研规范、文献、假设、设计、实施、数据、分析、解释、传播及其紧密领域适配层。

## 目录与所有权

- 稳定 Skill 统一放在 `skills/research/<skill-name>/`；每个 Skill 只有一个 canonical `SKILL.md`。
- 尚未稳定的 Skill 放在 `skills/in-progress/`；弃用 Skill 放在 `skills/deprecated/`。
- 面向使用者的说明放在 `docs/research/<skill-name>.md`，与稳定 Skill 一一对应。
- 长流程、低频分支和详细契约放在 Skill 自己的 sibling `references/`；脚本和测试跟随拥有它们的 Skill，不再依赖旧 Akira 总仓相对路径。
- 本仓库内部可以互相调用 Research family 的 Skill；仓库外能力只能按 Skill / capability 名称作为可选依赖，不通过跨仓相对路径读取正文。
- 第三方执行能力保持独立来源；不要把第三方 Skill 正文复制进本仓库。

## 独立安装边界

本仓库必须能够被 `npx skills add <repo> --skill '*'` 独立发现和安装。基础科研流程不得要求 Akira Lattice 或旧 `Akira-TL/skills` checkout 存在。

外部浏览器、文档、专业软件、数据库或领域 runner 只在真实任务需要时按对应 Skill 契约发现；缺失时走显式 optional dependency / user approval 路径，不自动安装整套外部仓库，也不从模型记忆重建第三方实现。

## 修改规则

- 修改稳定 Skill 时同步修改对应 `docs/` 文档。
- 同一规则只保留一个 source of truth；Research database/schema、Git provenance 与 completion gate 的契约继续由 `skills/research/akira-research/` 统一维护。
- 人类可读科研表述继续使用现有学术术语规范，不因拆仓创造新的科研术语。
- Git 提交保持原子；脚本或 schema 修改运行相关 targeted tests，重大科研工作流修改再运行完整 Research test suite。

## 检查

若维护环境已安装 Akira Guard，使用其通用 Skill-repository 检查与 guarded commit；独立 checkout 至少执行：

```bash
npx skills add . --list
python -m unittest discover -s skills/research/akira-research/tests
python -m unittest discover -s skills/research/literature/tests
```

只运行与当前修改有关的更窄测试也是允许的；正式发布前再做完整验证。

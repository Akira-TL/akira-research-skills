# Repository instructions

本仓库是 Akira Research Skills 的 canonical source。它维护一个科研产品包中的两个主系列：由 `akira-research` 路由的研究者 / 作者侧 Research series，以及由 `akira-review` 路由的学术评议 Review series；两者可以复用窄科研能力，但不因同仓而自动共享作者内部状态。

## 目录与所有权

- 稳定 Skill 统一放在 `skills/research/<skill-name>/`；每个 Skill 只有一个 canonical `SKILL.md`。
- 尚未稳定的 Skill 放在 `skills/in-progress/`；弃用 Skill 放在 `skills/deprecated/`。
- 面向使用者的说明放在 `docs/research/<skill-name>.md`，与稳定 Skill 一一对应。
- 长流程、低频分支和详细契约放在 Skill 自己的 sibling `references/`；脚本和测试跟随拥有它们的 Skill，不再依赖旧 Akira 总仓相对路径。
- 本仓库内部可以互相调用 Research family 的 Skill；仓库外能力只能按 Skill / capability 名称作为可选依赖，不通过跨仓相对路径读取正文。
- 第三方执行能力保持独立来源；不要把第三方 Skill 正文复制进本仓库。
- 仓库级术语与边界见 `CONTEXT.md`；长期架构决定放 `.agents/adr/`；调用边界见 `.agents/invocation.md`。

## 独立安装边界

本仓库必须保持标准 `SKILL.md` 结构，并为每个 Skill 维护 `skiloom-package.toml`、由根目录 `skiloom-repo.toml` 定义仓库发现范围。canonical `SKILL.md` 只使用标准 Agent Skill frontmatter；执行器专属调用策略放在对应 metadata 文件中。运行时能力选择交给 `akira` Router，Package discovery、dependency resolution、source resolution、Registry / Store / Target 与 install/update/remove/sync/repair/recovery 全部交给 Skiloom public CLI。基础科研流程不得要求 Lattice 的本地 `skills/research` submodule 或旧 `Akira-TL/skills` checkout 作为运行时 source；当前 first-party source mode 由 Akira Catalog 明确为远端 Git `main`。

外部浏览器、文档、专业软件、数据库或领域 runner 只在真实任务需要时按对应 Skill 契约发现；缺失时走 `akira` Router → Skiloom Candidate plan → 用户授权 → accepted Target state，不自动安装整套外部仓库，也不从模型记忆重建第三方实现。

## 修改规则

- 修改稳定 Skill 时同步修改对应 `docs/research/<skill-name>.md` 文档。
- 新增或改变调用方式时同步标准 Skill frontmatter / `description`、`agents/openai.yaml` 的执行器调用策略与 `skills/research/README.md`。
- 同一规则只保留一个 source of truth；Research database/schema、Git provenance 与 completion gate 的契约继续由 `skills/research/akira-research/` 统一维护。
- 人类可读科研表述继续使用现有学术术语规范，不因拆仓创造新的科研术语。
- Git 提交保持原子；脚本或 schema 修改运行相关 targeted tests，重大科研工作流修改再运行完整 Research test suite。

## 检查

主要检查入口：

```bash
skiloom validate . --json
./scripts/check.sh
```

`skiloom validate` 负责标准 Package metadata、仓库发现规则与 canonical `SKILL.md` 的静态规范验证；运行时 discovery / install 由 `akira` Router 选择入口 Package，再通过 Skiloom `--plan --json` / `--yes --json` 流程核验和提交。正式提交继续使用 Akira Guard。

只运行与当前修改有关的更窄测试也是允许的；正式发布前再做完整验证。

## Agent skills

### Issue tracker

本仓库使用 GitHub Issues 作为 Spec、Ticket 与工程工作项的 canonical tracker。具体操作约定见 `docs/agents/issue-tracker.md`。

### Workflow roles

Matt 工程流程使用 canonical workflow role 名称映射到同名 GitHub labels。具体映射见 `docs/agents/triage-labels.md`。

### Domain docs

本仓库使用 single-context domain documentation：根目录 `CONTEXT.md` 为领域词汇与边界入口，长期架构决定继续保存在 `.agents/adr/`。具体消费规则见 `docs/agents/domain.md`。

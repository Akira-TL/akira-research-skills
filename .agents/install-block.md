# Akira Research 安装

Akira Research 只在真实科研任务需要时由 `akira` Router 选择入口 Package；Lattice 根安装器不预装 Research / Review series。Package discovery、dependency closure、source resolution、Registry / Store / Target 与生命周期动作统一由 Skiloom public CLI 管理。

当前 first-party 仓使用 Git `main` source mode。

## Research series

入口 Package：

```text
akira-tl/akira-research-skills/akira-research
```

先生成 Candidate plan：

```text
skiloom install akira-tl/akira-research-skills/akira-research --git main --scope user --plan --json
```

用户明确授权后提交：

```text
skiloom install akira-tl/akira-research-skills/akira-research --git main --scope user --yes --json
```

`akira-research` 的完整 Research series dependency closure 由各 `skiloom-package.toml` 与 Skiloom resolver 自动解析，不在安装文档手工枚举。

## Review series

入口 Package：

```text
akira-tl/akira-research-skills/akira-review
```

使用相同的 `--plan --json` → 用户授权 → `--yes --json` 流程。Review 与 Research 是平级入口，不因为同仓而自动把另一个变成 direct requirement。

## Target 与状态

运行时安装事实只来自 Skiloom accepted state。需要确认用户级 Target 时使用：

```text
skiloom status --scope user --json
```

不得通过旧 `~/.agents/akira-skills.json`、`~/.agents/sources/`、目录扫描或软链接存在性推断安装状态。

## 本地维护 checkout

本地 `skills/research` checkout 只用于开发、review、测试与固定 revision，不作为运行时 source。开发检查：

```bash
skiloom validate . --json
./scripts/check.sh
```

外部专业能力也遵守同一 Skiloom 生命周期边界；具体审计与科研 provenance 规则见 `akira-research/references/external-skills/POLICY.md`。

# ADR 0001：Research 仓库边界

## Status

Accepted

## Decision

`akira-research-skills` 独立维护完整 Research 系列。稳定 Skill 位于 `skills/research/`，对应文档位于 `docs/research/`。`akira-research` 负责顶层路由，其余 Research Skill 共享同一项目状态与版本记录。

通用浏览器、文档工具和第三方专业能力不复制到本仓；需要时由项目按需补充。

## Consequences

科研项目可以只安装 Research 系列；通用 Akira、Matt 和未来其他产品继续独立维护。

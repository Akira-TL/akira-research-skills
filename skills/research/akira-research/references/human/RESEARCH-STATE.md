# RESEARCH.md 人类格式

`RESEARCH.md` 是科研项目的人类首页和当前科研状态入口。本文件定义它的固定格式；科学语义继续由 `PROJECT-STATE.md`、Research Tree 与对应 owner Skill 负责。

## 固定路径与标题

路径固定为项目根目录 `RESEARCH.md`。文件必须且只能有一个一级标题：`# Research`。二级章节使用下面模板中的完整集合和顺序；不得增删、重排或另造同级章节。需要领域化展开时使用三级及更深层级。

## 完整模板

```markdown
# Research

## Objective

<当前研究试图理解、解释或解决什么；尚未形成具体 Research Question 时可保持宽泛，但不能留空。>

## Applicable Standards

不适用：当前没有额外正式规范。

## Current Loop

QUESTION

## Active Uncertainty

Question: <当前最需要证据区分的科学问题>

Competing explanations:
- <解释一>
- <解释二>

Discriminating gap: <当前哪一项证据缺口仍不能区分这些科学状态>

Best next evidence: <最有判别力且当前可取得的下一条证据>

## Current State

<用短小综合说明目前已经知道什么、仍不知道什么。>

## Active Work

<下一条真实科研动作、明确等待/blocker，或当前有边界的停止状态。>

## Open Threads

不适用：当前没有其他需要保留但暂不推进的开放问题。

## Key Decisions

不适用：当前没有仍影响研究路线的额外决定。

## Navigation

不适用：当前没有其他人类可读科研入口。

## References

- `.research/research.sqlite`
```

模板中的尖括号说明必须替换为真实内容，不能原样保留。`Current Loop` 使用 `PROJECT-STATE.md` 定义的允许值。`Active Uncertainty` 是否需要完整 competing explanations 结构由 Research Tree 契约决定；未形成多个竞争解释时仍必须写清当前 Question 和判别缺口，不能用“证据不足”冒充一个科学解释。

## Navigation

只放人会直接打开阅读的科研入口，并使用项目内相对 Markdown 链接。例如相关目录已经真实存在时，可以写：

```markdown
## Navigation

- [Research Tree](research-tree/README.md)
- [Literature](literature/README.md)
- [Hypotheses](hypotheses/README.md)
- [Designs](designs/README.md)
- [Data](data/README.md)
- [Analyses](analysis/README.md)
- [Communication](communication/README.md)
```

只列实际存在、具有阅读意义的入口，不为了模板完整制造空目录。`.research/`、缓存、机器审计文件和数据库不是这一章节的普通阅读入口。

## References

这里保存精确 provenance pointer、数据库位置、外部规范来源或其他不能放进 Navigation 的引用。机器内部路径使用内联代码记录，不包装成人类导航链接。详细科研知识继续进入其 owner artifact 或数据库，不把 `RESEARCH.md` 扩成日志。

## 显式空缺状态

必需章节不能空白。没有内容时使用公共 Human Artifact Contract 定义的状态：`不适用`、`未记录`、`未知` 或 `待确认`，并给出最短必要说明。

## 合格示例

一个尚处于问题形成阶段、没有额外正式规范和其他 artifact 的最小状态可以保留全部章节，并在 `Applicable Standards`、`Open Threads`、`Key Decisions`、`Navigation` 中明确写“不适用”，而不是删除这些章节。

## 典型错误

以下情况都不符合格式契约：

- 增加第二个一级标题；
- 把 `Current State` 放到 `Active Uncertainty` 之前；
- 因没有规范而删除 `Applicable Standards`；
- 留下空的 `Open Threads`；
- 新增 `## History`、`## Notes` 等同级章节代替 Git 历史或 owner artifact；
- 在 `Navigation` 中使用本机绝对路径或把 `.research/research.sqlite` 做成点击入口；
- 为了保留旧状态复制 `RESEARCH-v2.md`、`RESEARCH-final.md` 等版本文件。

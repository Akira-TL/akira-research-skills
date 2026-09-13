# Research Tree 人类总图

`research-tree/README.md` 是 Research Tree 的长期人类可读投影。canonical 科研关系仍只存在于 `research.sqlite` 的 Research Node / parent / Research Edge；本文件由 `research-db render-research-tree-view` 确定性生成，不作为第二套关系来源。

## 固定路径与结构

路径固定为：

```text
research-tree/README.md
```

一级标题固定为 `# Research Tree`，二级章节固定为：

```text
## Graph
## Node Index
```

`Graph` 只包含一张完整 Mermaid `flowchart`。Research Tree 很大时仍优先保持单一总图；`subgraph`、`direction`、节点位置和其他 Mermaid 布局语句只承担视觉归组，不表达科研关系。

## 科研关系与视觉归组

科研关系只由两类显式 edge 表达：

1. Research Node 的 canonical `parent_node_id` → Mermaid 实线 `-->`；
2. 已登记 `research_edges` → Mermaid 带 relation label 的虚线 `-. relation .->`。

没有 canonical parent / Research Edge，就不能为了让图看起来顺畅而新增箭头。尤其是同一父节点下的 competing Hypothesis，即使创建、关闭或分析时间不同，也保持 sibling；时间先后、Node ID、Markdown 顺序和图形位置都不能生成 H1 → H2 → H3 之类科研关系。

`subgraph` 默认可用于把同一父节点、同一 Node kind 的多个 sibling 放在一个视觉区域。改变 `subgraph`、方向或位置，只要显式 edge 集合不变，就不改变科研语义。

## Node Index

总图下方固定提供 Markdown 节点索引。每个 Node 至少显示：

- Node ID；
- Node kind；
- workflow status；
- 人类可读 label；
- 已存在 canonical human artifact 时的项目内相对链接。

没有 human artifact 的 Node 显示 `—`，不制造空文件。artifact link 从 `research-tree/README.md` 出发使用项目内相对路径，不进入 `.research/` 机器内部区。

## 生成与校验

Research Tree 新增、改动 Node、parent 或 scientific relation 后，运行：

```bash
research-db render-research-tree-view
```

随后 `research-db validate --completion` 会比较人类总图与 canonical Research Tree：

- 缺少 canonical Node / edge → fail closed；
- 人类图额外出现数据库没有的 Node / edge → fail closed；
- `subgraph`、方向或其他不改变 edge 的视觉调整 → 允许；
- 断开的 artifact 相对链接、越出项目或指向 `.research/` 的人类导航 → 按 Human Artifact Contract 阻断。

validator 允许不改变 edge 的视觉布局差异，是为了把科研语义与 Mermaid 排版解耦；`research-tree/README.md` 仍是 generated human view，不成为第二个 editable authority。需要长期保留的布局规则应修改 renderer 或其明确配置，再重新生成；科研关系则必须先通过 Research Tree 的正式记录接口更新。

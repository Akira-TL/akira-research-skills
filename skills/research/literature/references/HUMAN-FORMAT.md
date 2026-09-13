# Literature 人类格式

本文件是 Literature 人类阅读区的唯一格式 authority。论文如何发现、阅读、重建与批判见 [`../READING-PROTOCOL.md`](../READING-PROTOCOL.md)；结构化科研事实、阅读状态和证据关系仍以 `research.sqlite` 为准。

## 1. 人类阅读区

用户日常阅读入口固定为：

```text
literature/
├── README.md
├── papers/
│   ├── <论文题名> - <第一作者> - <年份>.md
│   └── <论文题名> - <第一作者> - <年份>.pdf   # 可选
└── collections/
    └── <主题>.md
```

机器来源、XML、HTML、JSON、表格、Supplementary Information、Source Data 和其他科研 artifact 继续保存在 `.research/artifacts/papers/<paper-id>/`，不作为普通人类导航入口。

人类文件不使用 `final`、`latest`、格式版本号或其他文件名副本表达历史。Markdown 内容历史由 Git 管理；阅读确认绑定 Git 内容对象。只有文件系统非法字符允许做必要替换，不用 Paper ID、内部缩写或 Agent 自造编号代替正常书目信息。

## 2. `literature/README.md`

只要 `literature/` 存在，固定入口 `literature/README.md` 就必须存在。一级标题和二级章节严格如下：

```markdown
# Literature

## Navigation

- [Research](../RESEARCH.md)

## Papers

- [<论文题名>](<papers/<论文题名> - <第一作者> - <年份>.md>) — <最短阅读用途/状态说明>

## Collections

- [<集合名称>](collections/<集合文件>.md) — <最短组织目的说明>
```

`Papers` 必须覆盖 `literature/papers/` 下全部正式 Markdown note；`Collections` 必须覆盖 `literature/collections/` 下全部 collection。若当前没有某一类对象，保留对应 H2 并写 `不适用：当前没有……`，不得删除章节。

文件名含空格时，Markdown 链接目标使用 `<...>` 包裹，例如：

```markdown
[论文标题](<papers/Long Paper Title - Wang - 2026.md>)
```

## 3. Collection

Collection 只是人类阅读索引，不建立第二套文献状态。固定路径为 `literature/collections/<主题>.md`，格式为：

```markdown
# Collection: <集合名称>

## Navigation

- [Literature](../README.md)
- [Research](../../RESEARCH.md)

## Purpose

<说明该集合围绕什么 Research Question、方法、主题或人工阅读目的组织；不要把数据库状态复制成第二套事实。>

## Papers

- [<论文题名>](<../papers/<论文题名> - <第一作者> - <年份>.md>) — <为什么属于本集合>
```

`Papers` 只链接 `literature/papers/*.md` 的人类论文 note，不链接 `.research/`、机器 artifact、临时文件或另一个 Collection。一个 Paper 可以出现在多个 Collection；这只是人类导航关系，不改变 canonical Paper identity、reading priority 或 evidence status。

## 4. 单篇论文 note

固定路径为：

```text
literature/papers/<论文题名> - <第一作者> - <年份>.md
```

文件名中的第一作者与年份必须和正文 metadata 一致。可选人类 PDF 使用完全相同的基础名：

```text
literature/papers/<论文题名> - <第一作者> - <年份>.pdf
```

如果 metadata 的 `本地全文` 给出本地 PDF 链接，它必须指向存在的同名 PDF；没有可供人直接阅读的 PDF 时明确写“当前无可用 PDF”，不要创建伪链接。

单篇 note 使用**类型标记**而不是格式版本标记：

```text
<!-- akira:literature-note -->
```

一级标题必须且只能是原始论文题名。固定 metadata 字段和顺序不得修改；未知或不适用的值显式写 `—`、`无`、`未记录` 或具体原因，不留空。

完整模板：

```markdown
# 原始论文题名

<!-- akira:literature-note -->

| 项目 | 信息 |
| --- | --- |
| 中文译题 | — |
| 第一作者 | Wang |
| 期刊 / 会议 | Journal Name |
| 年份 | 2026 |
| DOI | 10.xxxx/xxxx；无则写 — |
| PMID / PMCID | 有则填写；无则写 — |
| Paper ID | P000123 |
| 论文类型 | 原始研究 / 综述 / 方法论文 / ... |
| 当前阅读用途 | 证据核验；研究设计学习 |
| 本地全文 | [PDF](<原始论文题名 - Wang - 2026.pdf>)；没有则写当前无可用 PDF |

<!-- akira:user-read:top -->
- [ ] **我已阅读并确认当前版本**
<!-- /akira:user-read:top -->

## 三句话总结

1. 这篇论文解决什么问题。
2. 它怎么解决。
3. 最重要的实验结果及结论边界是什么。

## 为什么值得读

<与当前项目 / Active Uncertainty 的关系，以及为什么值得投入阅读。>

## 论文逻辑

### 研究背景

<内容>

### 已有工作与不足

<内容>

### 作者的问题

<内容>

### 核心思路

<内容>

## 方法拆解

### 输入 / 研究对象

<内容>

### 核心过程

<内容>

### 输出 / 测量

<内容>

### 关键参数与假设

<内容>

### 复现信息

<内容>

## 实验逻辑

### 实验 1：按论文实际内容命名

<为什么做 → 怎么做 → 数据直接得到什么。>

## 数据直接显示什么

<只写 Observation，不混入作者解释或 Agent 推论。>

## 作者如何解释

<忠实记录作者 Claim。>

## 我们的证据评估

### 直接支持什么

<内容>

### 间接支持或限定什么

<内容>

### 没有建立什么

<内容>

### 主要问题与替代解释

<内容>

## 关键图表与定位

- <图 / 表 / Supplement / 方法位置> — <回答什么、为什么重要、在哪里回原文核验>

## 可复用内容

- <方法 / protocol / 代码 / 数据 / 参数 / 模型>

## 科研启发

<对 Research Question / Hypothesis / Analysis / Design 的新线索；不得冒充作者结论。>

## 结论边界

<当前最窄、可辩护的结论。>

## 我的笔记

> 以下区域仅供用户手工记录。Agent 只初始化边界，不修改、重写、整理、总结或清空其中内容。

<!-- akira:user-notes:start -->

<!-- /akira:user-notes:end -->

<!-- akira:user-read:bottom -->
- [ ] **我已阅读并确认当前版本**
<!-- /akira:user-read:bottom -->
```

固定 H2 必须完整且按上述顺序出现。论文实际有几个实验、几个图、几个假设以及每节写多长都属于科学内容，不做机械配额；具体展开使用 H3+。`## 我的笔记` 内属于用户的 Markdown 标题不参与 Agent 结构门禁。

## 5. 用户确认与用户笔记

顶部和底部复选框是同一用户确认状态的两个入口。只有用户实际勾选后运行 `research-db sync-user-reading` 才能形成确认事件；Agent 不替用户勾选。

确认使用规范化后的 Git 内容对象 ID：两个复选框状态与 `akira:user-notes` 用户专属内容不改变 Agent 正文版本身份。因此用户继续补写自己的笔记不会使既有确认失效；Agent 修改论文总结、证据评估、结论边界等生成区域则形成新的阅读正文版本，旧确认不能自动继承。

Agent 更新 note 时逐字保留 `akira:user-notes` 边界内已有内容。

## 6. 历史迁移

当前格式不把版本号写进文件身份。项目从旧 schema 迁入本契约时：

1. `research-db migrate` 先记录迁移前真实 Git HEAD 作为 Literature human-format legacy baseline；
2. 对已经使用历史版本型 Literature note marker 的文件，只确定性替换 marker，本体正文、metadata、用户笔记和确认区域不改写；
3. 更早的无 marker 旧 note 只有在迁移 baseline 中已经存在、且迁移后完全未修改时才可继续 grandfather；
4. 旧 note 一旦在迁移后被 Agent 实质编辑，就必须整体采用当前固定格式；
5. 新项目与迁移后新建 note 没有 legacy 豁免。

迁移 baseline 必须来自本契约启用前的真实 Git 历史；伪造、非祖先或已经处于当前 schema 的 baseline 不能用于绕过格式门禁。

## 7. 合格与不合格边界

合格示例：`literature/README.md` 可以直接进入某篇 note 或某个 Collection；Collection 再进入具体 note；note 中的本地 PDF 链接指向同名 PDF。论文 note 的结构固定，但实验和方法细节按真实论文使用 H3+ 展开。

代表性错误：

- 用 `final`、`latest`、文件名版本号或格式版本 marker 创建第二份 note；
- note 文件名的第一作者/年份与 metadata 不一致；
- README 或 Collection 漏掉实际存在的对象；
- Collection 的 `Papers` 链接到 `.research/`、XML、PDF 或临时文件而不是 human note；
- metadata 声称有本地 PDF，但链接不存在或基础名不同；
- 删除“不适用”的固定 H2，而不是显式说明状态；
- Agent 修改 `akira:user-notes` 中的用户内容；
- 用固定字数、固定实验数量或固定图表数量替代科学判断。

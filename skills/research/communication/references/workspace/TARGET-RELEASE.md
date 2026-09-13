# 目标期刊发布工作区契约

本文件是 Communication 中“中立稿件（venue-neutral manuscript）→ 目标期刊发布工作区（target release workspace）”的唯一工程契约。论文科学内容仍由同一 Communication Product 的规范可编辑源（canonical editable source）维护；目标期刊工作区只负责把该内容转换成当前期刊所需表示，不建立第二份可独立修改的科学稿件。

## 1. 普通草稿保持中立

目标期刊尚未确定时，论文可以完整起草、审阅和修订。此时只需要：

```text
communication/<article-code>/
└── <canonical editable source>
```

不要为了“以后可能投稿某期刊”提前把普通草稿改造成某个期刊的章节、字数、匿名、引用格式或文件结构。Document Type 和科学论证先由 Communication workflow 决定；只有用户真正进入投稿、终稿转换或其他明确目标期刊准备时，才建立 target release workspace。

同一逻辑内容只有一个 canonical editable source。它可以是适合项目的 Markdown、LaTeX 或其他文本/代码型 source，但必须可以由 Git 正常管理；DOCX、XLSX、PDF、PPTX 等生成表示不能作为 canonical editable source。

## 2. 先登记稳定期刊代码

目标期刊确定后，先从当前官方来源核验期刊身份与 Author Instructions，再登记项目内稳定短代码：

```json
{
  "code": "NC",
  "name": "Nature Communications",
  "official_source": "<当前官方期刊/作者指南来源>",
  "checked_at": "<含时区的 ISO 8601 时间>"
}
```

使用：

```text
research-db record-journal
```

代码由当前项目明确登记，不由 Agent 每次临场重新缩写。同一期刊已经登记 `NC` 后，后续继续使用 `NC`；不能再建立 `NComms`、`NatComm` 等第二别名。同一个代码也不能改指另一期刊。

## 3. 固定目录

一个文章可以同时准备多个目标期刊，但都消费同一 canonical source：

```text
communication/<article-code>/
├── <canonical editable source>
├── NC-release/
│   ├── manifest.json
│   ├── journal.json
│   ├── build.py
│   ├── template.tex       # 仅真实需要且该文件本身是模板 source 时
│   └── QA.md
└── iMeta-release/
    └── ...
```

目标目录固定为：

```text
<journal-code>-release/
```

`NC-release/` 表示“面向 NC 的 target release workspace”，不是“这篇论文已经公开发表”。真正公开发布的 Git tag 由独立发布契约管理，不能因为目录名带 `release` 就宣称论文已经正式发布。

共享、多期刊复用的 build library / validator 继续放在 `scripts/communication/` 或项目既有代码区；只属于某一目标期刊的 entrypoint、配置、模板 source、manifest 与 QA 依据放在该 `<journal-code>-release/` 内。

## 4. `manifest.json` 是 target build 身份

每个 target workspace 必须有固定的 `manifest.json`：

```json
{
  "journal_code": "NC",
  "canonical_source": "communication/yak-ecology/manuscript.md",
  "source_commit": "<包含当前 canonical source 的 Git commit>",
  "config": "journal.json",
  "build_sources": ["build.py"],
  "template_status": "provided",
  "templates": ["template.tex"],
  "qa_evidence": ["QA.md"],
  "generated_outputs": [
    "manuscript.tex",
    "manuscript.docx",
    "source-data.xlsx",
    "manuscript.pdf"
  ]
}
```

字段职责：

- `journal_code`：必须等于已登记短代码，也必须与 `<journal-code>-release/` 目录一致；
- `canonical_source`：必须指向该 Communication Product 唯一的 canonical editable source；
- `source_commit`：本次 target build 实际消费的 **Communication source commit**；它与 `communication_products.source_commit` 的“传播开始前科学证据冻结 commit”不是同一个概念；
- `config`：目标期刊转换配置；
- `build_sources`：本目标需要的转换/构建入口，至少一个；
- `template_status`：`provided | not_provided | not_applicable`；只有 `provided` 时 `templates` 才非空；
- `templates`：目标期刊正式模板或项目维护的目标格式模板 source；
- `qa_evidence`：当前 target build 的 QA 依据入口，至少一个；
- `generated_outputs`：该 build 预期产生的交付表示名称。这里只声明目标，不把这些生成文件提升为 source。

`config`、`build_sources`、`templates`、`qa_evidence` 都必须是 workspace 内的真实文件；不能用绝对路径、`..` 或 `.research/` 中的临时文件替代。

完成文件后运行：

```text
research-db record-target-workspace
```

登记 bundle 只需要：

```json
{
  "slug": "yak-ecology",
  "journal_code": "NC",
  "source_commit": "<manifest 中同一个 Communication source commit>"
}
```

登记时会把 manifest/config/build source/template/QA 文件的 Git content OID 固定下来。之后这些文件发生变化，target workspace 自动进入 stale 状态，必须重新 build、重新 QA，再重新登记；不能静默沿用旧 target provenance。

## 5. 生成表示不是可编辑 authority

以下两类文件都按 generated representation 处理：

1. DOCX、XLSX、PDF、PPTX、ODT、ODS、ODP 等复合/页面型输出；
2. `manifest.json` 的 `generated_outputs` 明确声明为 build 结果的任何文件，包括 `.tex` 等纯文本格式。

如果生成后的 DOCX、XLSX、PDF、LaTeX 或其他交付表示有内容或排版问题，处理顺序固定为：

```text
canonical source / config / build source / template source
→ 修改真正 authority
→ rebuild
→ QA
→ record-target-workspace
```

不能打开生成结果做一点点手工修正，再把它当成新的 canonical content。只要 `.tex` 是 generator 的输出，它也遵守这一规则；如果某个 `.tex` 本身就是项目明确选择的 canonical editable source，则它直接属于上层 Communication Product，而不是同一 target workspace 的 generated output。

目标工作区因此保存“如何生成”和“如何验收”，不保存可被继续手工维护的生成副本。

## 6. Source 与 build drift

Target workspace 的 readiness 同时绑定两类状态：

- canonical source 的 Git commit；
- manifest/config/build/template/QA 文件的 Git content OID。

任一层改变后，旧 target registration 不再代表当前内容：

```text
canonical source 改变
→ communication_target_source_drift

manifest/config/build/template/QA 改变
→ communication_target_build_source_drift / manifest drift
```

这不是要求稿件停止修改，而是要求每次实际修改后重新生成目标期刊版本。普通 venue-neutral 草稿没有 target workspace 时，不受这一 target drift gate 约束。

## 7. 与投稿工作流的关系

`<journal-code>-release/` 建立的是**目标格式转换与交付准备边界**。目标期刊当前具体要求仍通过 `research-standards` 和官方 Author Instructions 核验；Submission Package 负责作者、匿名、declaration、Figure/Supplement、Data/Code、cover letter、reviewer suggestion 等当前真实 deliverables。

目标期刊选择发生变化时，不复制 canonical manuscript：登记新的 journal code，并新增对应 `<journal-code>-release/`。例如：

```text
communication/yak-ecology/
├── manuscript.md
├── NC-release/
└── iMeta-release/
```

两个 target 都可以存在，科学正文仍只有 `manuscript.md` 一个 editable authority。

## 8. 完成检查

Target workspace 可以视为当前可用，至少满足：

- journal code 已登记，且同一期刊没有第二别名；
- workspace 恰好使用 `<journal-code>-release/`；
- manifest 的 journal/source/source_commit 与数据库一致；
- canonical source 位于 product workspace，而不位于任何 target release workspace；
- manifest/config/build source/template/QA 都存在、受 Git 管理并与登记 content OID 一致；
- canonical source 自 `source_commit` 后没有发生未重建的变化；
- target workspace 没有保存 DOCX/XLSX/PDF/PPTX 等生成表示，也没有保存 manifest 声明的其他 generated output；
- QA 依据存在；真正页面型交付物还按 `RENDERED-OUTPUT-QA.md` 执行实际渲染验收。

这些检查证明的是 source/build provenance 一致，不代表论文已经投稿、接收或公开发表。

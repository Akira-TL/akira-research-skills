# Communication 正式稿件 Git Tag

本文件是 Communication Product 面向目标期刊形成正式 manuscript checkpoint 与真实公开 release 时的唯一 Git tag authority。Target workspace 的目录、manifest、build source 与生成物边界见 [`TARGET-RELEASE.md`](TARGET-RELEASE.md)。

这些 tag 是**科研稿件版本锚点**，不是软件包 `vX.Y.Z` 发布 tag。Core 对尚未产生正式软件发布产物的失败 release tag 可能允许重建；本契约更严格：`research-db tag-communication-release` 一旦成功返回，稿件 tag 的历史含义即固定，不得移动、force 更新、删除后重建或复用名称。

## 1. 唯一版本模型

正式稿件只使用：

```text
<版本号>.<修订号>
```

例如：

```text
1.0
1.1
1.2
2.0
2.1
```

它不是语义化版本（Semantic Versioning, SemVer）：没有 patch 位，不使用 `v1.0`，也不使用 `1.0.1`。

同一个 `(article-code, journal-code)` lineage：

1. 首个正式 checkpoint 必须从 `1.0` 开始；
2. 同一整数 baseline 内只允许修订号连续 `+1`，例如 `1.0 → 1.1 → 1.2`；
3. 新整数 baseline 只允许从当前 baseline 进入下一整数的 `.0`，例如 `1.2 → 2.0`；
4. 新整数 baseline 不是 Agent 根据“改得很多”自行判断的结果，必须记录本次用户明确批准，或指向已有的显式项目决定；
5. 换目标期刊后，新期刊拥有独立 lineage，并重新从 `1.0` 开始。

`final`、`latest`、`new`、`accepted`、`published-final` 等状态词不进入正式稿件版本名。

## 2. Tag 名称

普通 manuscript checkpoint：

```text
<article-code>/<journal-code>-<版本号>.<修订号>
```

例如：

```text
yak-ecology/NC-1.0
yak-ecology/NC-1.1
yak-ecology/iMeta-1.0
```

`<article-code>` 直接使用 `communication_products.slug`，因此不再额外增加 `comm/` 或抽象 `product/` 前缀。`<journal-code>` 必须使用项目 journal registry 已登记的精确拼写，并对应同一 Product 下的 `<journal-code>-release/`。

所有正式稿件 tag 必须是 annotated tag。不得用 lightweight tag 代替。

## 3. 公开 Release

只有稿件已经真实公开时，才允许为已有 checkpoint 增加：

```text
<article-code>/<journal-code>-<版本号>.<修订号>-release-<YYYYMMDD>
```

例如：

```text
yak-ecology/NC-1.2-release-20260913
```

`release` 不是“准备投稿”“已经提交”“已接收”或“我认为完成”的同义词。创建 public release tag 必须同时满足：

- 对应基础 checkpoint 已存在；
- 日期是已经发生的真实公开日期，不允许未来日期；
- 有用户明确确认，或有可核验公开信息支持该日期；
- release tag 与基础 checkpoint 指向**同一个 Git commit**。

如果公开前 canonical content 又发生变化，不能把旧 checkpoint 重新指向新内容；必须先形成新的修订或新的、经批准的整数 baseline，再对那个 checkpoint 建立 release tag。

## 4. 唯一创建入口

正常工作流只使用：

```bash
research-db tag-communication-release [bundle]
```

普通 checkpoint bundle：

```json
{
  "slug": "yak-ecology",
  "journal_code": "NC",
  "version": "1.1"
}
```

新整数 baseline：

```json
{
  "slug": "yak-ecology",
  "journal_code": "NC",
  "version": "2.0",
  "baseline_approval_source": "user",
  "baseline_approval": "用户明确确认该稿件形成新的正式版本基线。"
}
```

若已有正式项目决定，可使用 `baseline_approval_source=project_decision`，并在 `baseline_approval` 中保存足以定位该决定的说明。不得写空泛的“Agent 认为应该升级”。

公开 release：

```json
{
  "slug": "yak-ecology",
  "journal_code": "NC",
  "version": "1.2",
  "release_date": "2026-09-13",
  "release_evidence_source": "public_source",
  "release_evidence": "已核验的正式出版页面或 DOI metadata 来源。"
}
```

用户直接明确确认公开日期时使用 `release_evidence_source=user_confirmation`，并保存用户确认的最小必要表述。

## 5. 创建前门禁

普通 checkpoint 创建前必须同时满足：

- 工作树 clean；
- Communication Product、journal code 和 `<journal-code>-release/` 已登记；
- canonical editable source 仍与 target source commit 一致；
- manifest、config、build source、template source、QA evidence 与登记 OID 一致；
- manifest 提供非空 argv `build_command`，并用 `{output_dir}` 把构建结果定向到临时目录；
- 创建 checkpoint 时实际执行该 build command，且 `generated_outputs` 全部真实生成；
- target workspace 没有保存 generated DOCX/XLSX/PDF/生成型 LaTeX，也没有 manifest 外的第二份稿件；
- 版本序列合法且 tag 名未使用过。

该门禁验证的是**当前提交具有可重建 target package 所需的受控 source/build state，并且声明的 build 在当前环境真实可执行**。临时构建输出在检查结束后删除，不进入 source tree。真正提交到期刊前仍需按 Submission Package 与 Rendered Output QA 对实际交付物执行 build/render/页面检查；不能把“tag 创建成功”解释成期刊 package 已自动通过全部人工/视觉 QA。

## 6. 不可变性与 Completion

`research.sqlite` 保存每个正式 tag 的：

- target workspace；
- 版本号与修订号；
- checkpoint / release 类型；
- release 日期及其 evidence；
- 新整数 baseline 批准依据；
- 被 tag 的 commit OID；
- annotated tag object OID。

Completion 会反查真实 Git refs：

- tag 缺失 → fail；
- tag 被改成 lightweight → fail；
- tag object OID 改变 → fail；
- 指向 commit 改变 → fail；
- `<article-code>/...` 下出现非法命名或未登记 tag → fail；
- public release 与基础 checkpoint 不同 commit → fail。

因此正常修正方式永远不是“移动旧 tag”，而是保留旧锚点并形成下一个合法版本，例如：

```text
NC-1.1
→ 内容继续修改
→ NC-1.2
```

已经公开后的正式修订同理：形成新的 checkpoint，再在真实公开后建立新的 `release-YYYYMMDD` tag。

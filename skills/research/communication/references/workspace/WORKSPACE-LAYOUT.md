# Communication 工作区布局

本文件定义科研传播产物在项目文件系统中的职责边界。目标是让作者、合作者或审稿准备时首先看到真正需要阅读和交付的内容，同时把审计、追溯、验证和可重放生成代码保留在同一科研溯源体系中，但不与人类传播视图混放。

## 1. 三个物理区域

一个 Communication Product 使用同一个 `slug` 关联三类位置：

```text
communication/<product-slug>/
.research/communication/<product-slug>/
scripts/communication/
```

三者职责不同：

- `communication/<product-slug>/`：人类传播视图。保存作者、合作者、审稿人或目标受众需要直接阅读、检查或提交的传播产物；
- `.research/communication/<product-slug>/`：内部传播支持区。保存材料盘点、引用/方法/一致性审计、追溯表、验证报告、reviewer-style stress test 等主要供 Agent 或科研审计使用的支持 artifact；
- `scripts/communication/`：可重放生成器、转换器与 validator。代码保持在正常工程代码区，不因属于某个传播产品就复制进人类传播目录。

`<product-slug>` 是当前 Communication Product 的稳定技术标识，不代表某个固定研究方向、论文类型或领域名称。每个真实传播产品根据自身目的选择 slug；不得把示例 slug 当作目录规范。

## 2. 人类传播视图

`communication/` 是项目级的人类传播入口。其顶层保持简单：

```text
communication/
├── README.md                 # 可选：多产品导航
└── <product-slug>/
    ├── README.md             # 可选：该产品的人类入口
    ├── <主要交付物>
    ├── figures/              # 按需
    ├── supplement/           # 按需
    └── submission/           # 仅真实投稿/提交 package 需要时出现
```

这里不规定某种论文必须叫 `manuscript.md`，也不规定 Figure、Supplement 或 submission 子目录必须存在；结构随真实传播类型和 venue 要求出现。唯一固定原则是：**用户进入 `communication/<product-slug>/` 时，应主要看到当前传播产品本身，而不是生成和审计它的后台文件。**

适合放在这里的内容包括：

- manuscript / thesis chapter / report / review 正文；
- 面向受众的摘要、图、表、图注与必要 Supplement；
- reviewer response、clean/marked manuscript 等真实 revision deliverable；
- 真实 submission package 中要求交付的文件；
- 为人类阅读提供导航的 README。

## 3. 内部传播支持区

`.research/communication/<product-slug>/` 保存传播过程中的内部工程与审计产物。可以按真实需要使用例如：

```text
.research/communication/<product-slug>/
├── materials/
├── audit/
├── traceability/
└── validation/
```

这些子目录是常见职责示例，不要求空目录预先创建，也不要求所有产品采用相同层级。判断标准是 artifact 的主要使用者和职责，而不是文件扩展名：

- citation / methods / integrity / consistency audit → `audit/`；
- Claim、Figure、source-data 或 artifact mapping → `traceability/`；
- validator JSON、QA report、机器可读检查结果 → `validation/`；
- 写作材料盘点、section skeleton、内部写作导航 → `materials/`。

内部支持 artifact 仍可作为 `communication_artifacts` 登记、进入 Git 完整性门禁和长期溯源；隐藏目录只改变人类阅读界面，不降低其审计地位，也不会把它提升为 canonical scientific evidence。

## 4. 版本与历史

普通 draft 的历史版本由 Git 保存，不默认建立 `archive/`，也不通过 `*_v0.md`、`*_v1.md` 的无限复制代替版本控制。当前工作区优先保留正在使用的有效版本。

只有具有独立外部身份或真实交付意义的历史状态，例如首次投稿 package、正式 revision、resubmission、accepted manuscript，才继续作为独立 Communication Product 或明确的 submission/revision artifact 保存。

## 5. 产品边界与数据库登记

同一 Communication Product 的人类交付物和内部支持 artifact 可以分布在上述不同区域，但必须由同一个 `communication_products.slug` 关联，并按实际职责登记 `communication_artifacts`。

新传播产品从开始产生多个 artifact 时就按本布局放置，不先在一个目录平铺几十个文件后再依赖 README 解释。已有项目需要重组路径时，先在文件系统/Git 中完成真实移动，再使用 `research-db relocate-communication-artifact` 同步 provenance；不要直接手工改 SQLite。该操作只更新既有 artifact 的路径，不改变 role、`timing_role`、`source_commit` 或 Communication Product 定义。已完成产品的 `source_support` 路径继续由 pre-communication source commit 证明，因此当前 fail closed，不允许用 relocation 改写。

完成判据：用户能从 `communication/<product-slug>/` 直接识别主要阅读/交付内容；内部支持文件位于 `.research/communication/<product-slug>/`；可重放代码位于 `scripts/communication/` 或项目既有代码区；所有需要 provenance 的 artifact 与实际路径一致。
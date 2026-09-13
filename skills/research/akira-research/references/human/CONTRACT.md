# Research 人类可读科研文件契约

本文件是 Research family 长期人类可读科研文件的公共格式契约。各 owner Skill 继续定义自己的科学语义和具体模板；这里仅定义所有长期人类文件共同遵守的阅读、导航、版本与可编辑来源边界。

## 1. 人类文件有稳定身份，不用文件副本表示版本

同一个科研对象保持稳定路径和稳定文件名。普通修改历史由 Git commit 保存，不通过 `v1`、`v2`、`final`、`latest`、`new` 等文件名或目录名复制当前内容。

若某类文件使用机器可识别的类型 marker，marker 只表达文件类型，不携带格式版本号。格式演化由 Git 历史和迁移规则处理，不把 `:v1`、`:v2` 写成人类 artifact 身份。

完成标准：人看到一个科研对象只有一个当前 canonical 人类入口；需要追溯旧内容时使用 Git，而不是寻找多个版本副本。

## 2. 结构严格，科学内容由主模型判断

每个 owner Skill 的 human format reference 必须给出一份完整可复制模板，并明确：

- 固定路径与文件命名；
- 唯一一级标题（H1）；
- 必需二级章节（H2）及其顺序；
- 每个章节的科学职责；
- 允许扩展的位置；
- 缺失、不适用、未知和待确认信息的表达；
- 合格示例与代表性错误示例。

必需章节不得留空。没有内容时使用显式状态，而不是删除章节或留下空白。公共推荐形式为：

- `不适用：<原因>`：该字段对当前对象不适用；
- `未记录：<原因>`：历史事实或来源没有留下可恢复记录；
- `未知：<当前未知内容>`：科学事实当前未知；
- `待确认：<需要确认的事实或输入>`：已有明确确认动作，但尚未取得结果。

H3 及更深层级可以按真实领域内容展开。机械 validator 只检查低歧义结构、链接和 provenance，不检查 Hypothesis 是否优秀、Discussion 是否充分或 Claim 是否科学成立。

## 3. 相对链接组成可导航的人类科研图

长期人类 Markdown 使用项目内相对 Markdown 链接连接相关科研对象。绝对本地路径、`file://` 路径和越出项目根目录的链接不能作为 canonical 导航。

`.research/` 是机器状态和内部支持区。人类文档可以用内联代码或文字说明其中的 provenance pointer，但普通阅读导航不得把 `.research/` 文件作为用户点击进入的主要目标。

每个 owner 负责写入创建时已经确定的上游关系；可更新索引负责反向发现。核心科研对象的目录 README 固定区分 `Objects` 与 `Relations`：前者列 canonical 对象，后者用项目内相对链接暴露数据库或 artifact 中已经确定的上/下游关系。目录 README 是科研对象阅读图，不是裸文件清单。

完成标准：复制或克隆整个项目后，人类导航仍可工作；validator 能识别断开的本地链接和越过人类/机器边界的导航。

## 4. 冻结 artifact 的科研内容优先于导航便利

Hypothesis、Design 或其他受结果可见前 freeze 约束的 artifact，一旦冻结，不为了后来出现的下游对象补写链接。后来产生的关系由：

1. 新的下游 artifact 指回已知上游；
2. 可更新目录索引提供反向入口；
3. Research Tree 展示当前完整关系。

因此“导航完整”不构成改写冻结科研内容的理由。

## 5. 一个逻辑内容只有一个 canonical editable source

同一逻辑内容只能明确一个可直接编辑的 authority。DOCX、XLSX、PDF 以及从其他 source 生成的 LaTeX、图、表或页面型文件是 build output；发现问题时修改 canonical source 或 generator，再重新 build。

纯文本格式本身不决定是否可编辑。例如 `.tex` 可以被选为 canonical editable source；但一旦它由另一份 source 自动生成，就属于 generated output，不再手工局部修改。

完成标准：任何交付表示都能说明自己的 editable authority 或 producer，不存在两个可独立编辑、可能相互漂移的“正文真相”。

## 6. References 与 Navigation 分工

`Navigation` 用于人实际点击阅读的科研入口，目标必须属于人类可读层。

`References` 用于 provenance、数据库、外部资源或其他精确 pointer；机器内部路径可以在这里作为内联代码记录，但不能伪装成人类阅读链接。

owner Skill 可以采用不同章节名称，但必须在自己的 human format reference 中保持这种职责分离。

## 7. 历史 artifact 通过迁移基线兼容，不回写冻结正文

严格格式启用前已经存在的长期人类 artifact 可能属于结果前冻结或历史实施记录，不能仅为了新的排版契约被迫改写。旧项目执行包含人类格式契约激活 migration 的 `research-db migrate` 时，系统记录**迁移前 Git HEAD** 作为 legacy baseline。

仅当某个旧 artifact 同时满足以下条件时，允许继续保留迁移前格式：

- 该路径在真实 migration baseline commit 中已经存在；
- baseline 的数据库 schema 低于当前 schema，不能用当前版本伪造 baseline；
- baseline 之后该路径没有任何提交改写；
- 当前 working tree 内容也与 baseline 相同。

这类 artifact 作为历史记录保留，completion 将其列入 `grandfathered_paths`；新建的目录索引仍按当前格式提供反向导航。artifact 一旦在 migration 后被编辑，就立即失去 legacy 兼容资格，必须整体采用当前 owner `HUMAN-FORMAT.md`。新项目和 migration 后新建的 artifact 从一开始就没有豁免。

因此 legacy baseline 解决的是“不要为排版破坏历史科研版本”，不是允许长期维持两套可编辑格式，也不能通过手工写入 meta marker 绕过当前格式。

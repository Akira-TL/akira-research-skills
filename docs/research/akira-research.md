# akira-research

`akira-research` 是 Akira Research Skills 中 **Research series** 的顶层入口。它维护科研目标、当前主要不确定性、Research Tree、适用规范和停止边界，并按当前证据状态自主路由到文献、假设、设计、研究实施、数据、分析、解释或传播工作。学术评议属于平级的 Review series，由用户显式进入 `akira-review`，不会作为 Research Current Loop 的自动阶段。

## 适合什么时候用

- 从零建立一个可持续迭代的科研项目。
- 接管已有研究目录，重新理解现有数据、分析、文献和结论。
- 只给出科研目标，让 Agent 自主判断下一条信息增益最高的工作。
- 需要长期保留 Design freeze、Study deviation、Analysis provenance、Claim boundary 和 Git 历史。

## 使用方式

这是一个用户显式启动的 Skill。通常只需要调用 `akira-research` 并给出项目路径与研究目标；后续子工作流由 Router 自主选择。项目用 `RESEARCH.md` 保存短小的当前状态并作为人类科研首页，用 `.research/research.sqlite` 保存结构化科研 provenance。长期人类科研文件采用稳定格式和项目内相对 Markdown 导航；普通历史由 Git 保存，不通过复制 `v1`、`final`、`latest` 等文件维护版本。

## 关键边界

学术语言检查不改写机器证据。对于全文仅含逐行 `字段=40位或64位十六进制散列` 的 `.txt` 记录，字段保持原样，不作为人类科研正文检查；这项识别同时用于分析执行前和完成门禁。只要混入正文、注释、非散列值或格式不完整，仍按原规则检查整个文件；Markdown 正文中的技术字面量仍需使用代码标记。不得按文件名或实施附件角色整体豁免可能含有人类解释的材料。

它不是固定阶段流水线，也不要求每个项目都经过 Hypothesis、Study 或全部子 Skill。`REVIEW` 不进入 Research Current Loop：用户明确需要导师式学术评议、独立同行评议、创新性核验或修回再审时，切换到平级 `akira-review`，由 Review 自己固定信息边界。Review Result 返回后先由用户决定是否采纳；只有用户决定处理具体 Concern 后，`akira-research` 才把实际工作路由到 Literature、Design、Study、Data、Analysis、Interpretation 或 Communication，并由这些作者侧流程更新 canonical scientific state。

只有存在真正的科学需要时才进入对应 Research 工作流；当下一条判别性证据必须依赖新样品、新实验、新权限或其他外部现实输入时，应在真实停止边界结束当前循环。

`RESEARCH.md` 的一级标题、二级章节集合与顺序是固定的人类界面；没有内容的必需章节必须明确写不适用、未记录、未知或待确认，而不是删除或留空。导航只指向真实存在的人类可读 artifact；`.research/` 保留为机器 provenance 与内部支持区。冻结的 Hypothesis / Design 等对象不会仅为了后来补导航而改写，后续关系由下游 artifact、可更新索引和 Research Tree 表达。目录级 Objects / Relations 导航索引只承担人类反向发现，不被 Communication completion 当作新的 scientific source；真实科研对象自己的 canonical artifact 仍正常进入科学来源漂移检查。

Analysis 完成门禁按分析模式区分结果要求。确认性分析进入 `completed` 时必须登记至少一个 `role=estimate` 的主要估计结果；明确不产生新估计的探索性综合、证据整理或图表数据组织可以只登记表格、图或其他真实结果产物，但仍必须满足数据输入、项目 Observation、执行 Attempt 和其他适用的 provenance 要求。不得为了通过门禁把既有汇总表或诊断文件改名为新的 estimate。旧项目从 schema v27 或更早版本正式迁移到 v28 时，会把迁移前 Git HEAD 作为 downstream artifact 兼容基线；只有当时已经被 Git 跟踪且迁移后完全未改动的历史 `data/` / `analysis/` 常规文件可以继续 grandfather，之后新增或编辑的未登记文件仍立即阻塞完成门禁。运行时能力或目录别名使用的 Git 软链接不参加“未登记科研文件”自动扫描；真正位于外部存储的科学数据仍必须通过正式 Dataset provenance 显式登记。文献 Candidate 已进入 `user_access_status=required` 后，completion 只保留“等待用户动作”这一项阻塞，不再为同一个 core/high Candidate 重复报告“高优先级未闭合”；原 reading priority 仍保持不变。已经不属于当前研究分支、但仍值得保留为相关文献的 Candidate，可以把 reading priority 降为 normal/low 并填写 `defer_reason`，此时保留其相关性与全文 provenance，但不再要求当前循环立即完成 Reconstruction/Critical Audit；core/high 不允许用 defer 绕过阅读闭合。从 schema v29 起，以论文为样本单位的系统性/元研究 Dataset 可通过 `record-dataset.paper_ids` 保存 Dataset↔Paper membership；这类 Paper 不因缺少 Candidate 回链就被误判成定向单篇 Literature target，但若同一 Paper 另行进入当前 core/high Candidate 队列，仍按 Literature 门禁处理。历史 Dataset/Analysis 若 canonical 人类入口仍位于旧路径，先创建规范的 `data/<slug>/README.md` 或 `analysis/<slug>/README.md`，再用 `research-db migrate-human-artifact-path` 仅迁移数据库 pointer；该操作不允许借机改写科学身份、状态、freeze、estimand 或结果。

科研项目根目录可以是代码仓库中的子目录（如 `research/`）。数据库路径仍相对科研根保存，科研根之外的仓库内代码用 `../scripts/...` 这类相对路径登记；Git 存在性、变更与冻结检查会自动换算到仓库顶层路径。托管 `.gitignore` 区块写在科研根目录自己的 `.gitignore` 中。

冻结对象由“冻结提交号 + 路径”识别，Git 跟踪的文件不再需要校验值。冻结对象当前内容与冻结版本逐字节相同时直接放行，中间改了又改回的提交只作为信息列出；否则冻结后的修改按提交逐个核对：路径迁移、去掉冗余校验值和执行状态更新（只改执行层状态、实现提交号与评审记录）这三类非实质修改用 `research-db record-freeze-revisions` 登记原因后放行；实质修改即使登记也仍然阻塞，须恢复冻结版本并建立新的 Analysis 或 Design；未登记的修改会作为阻塞项列出对应提交。这一规则同样适用于已冻结的 Hypothesis Set 与 Research Design 正文；`research-db freeze-revisions --pending` 可一次列出待登记的变化。

整体移动目录（包括把整个科研项目移入代码仓库的 `research/` 子目录）时，提交移动后运行 `research-db record-path-migration` 登记“迁移提交 + 旧前缀 + 新前缀”；命令会一次性改写数据库中的路径，之后核验旧冻结对象时按迁移记录回到旧路径查冻结提交，纯移动不算修改。

Communication Product 可以从 `completed` 终止为 `superseded`，用于保留已被新稿替代的历史产品；该 transition 不允许同时改写产品定义或科学 `source_commit`，且 superseded 后不能重新激活。历史传播 artifact 继续保留 provenance，但不再参与当前 completed-product 的科学源漂移检查或当前传播文本的学术语言门禁。中文科研项目仍可合法维护纯英文期刊稿；只有包含中文叙述的传播段落继续执行中文成熟术语检查。

高通量测序（Next-Generation Sequencing, NGS）作为领域执行能力接入现有分层，不新增科研阶段：真实建库和测序实施属于 `study`，测序数据处理属于 `data → ngs`，测序统计/生物信息推断属于 `analysis → ngs`，结果的科学解释仍属于 `interpretation`。

Research 需要认证/动态网页访问、DOCX 或科研演示文稿等仓库外 first-party 通用能力时，只声明能力需求，不复制浏览器、Word 或 PPT 实现。优先复用当前会话能力；当前会话不可用时把能力缺口交给 `akira` Router，由它按 first-party Catalog 选择入口 Package，并通过 Skiloom accepted Target state / Candidate plan 判断是否需要新增能力。需要状态变化时先展示 plan 并取得明确授权，再由 Skiloom 安装。用户拒绝安装、候选不能通过 Package admission，或当前执行器仍无法加载时，保留 canonical scientific content，并明确说明对应访问、格式生成或渲染验收没有完成，而不是在 Research 内临时建立第二套执行层。

当科研问题和方法已经由 Akira 确定，但缺少某个专业软件、数据库或领域工具的可靠执行知识时，可以按需推荐第三方 Skill。当前 K-Dense Scientific Agent Skills 只作为**按需发现源**：Agent 必须先核验具体 Skill 的来源、revision、license、脚本/网络/凭据和职责重叠，再由 `akira` Router 收敛为明确 Package candidate，并通过 Skiloom `--plan --json` 检查 source、dependency graph、Package admission 与 Target 影响；只有用户明确授权后才由 Skiloom 提交安装。Lattice 根安装器不会预装这些外部能力，无法通过 Skiloom admission 的 upstream 也不会由旧 installer 绕过。外部 Skill 只负责工具实现，不能反过来决定 Research Question、Design、Analysis scientific intent 或 scientific Claim。

# akira-research

`akira-research` 是 Akira 科研工作流的总入口。它维护科研目标、当前主要不确定性、Research Tree、适用规范和停止边界，并按当前证据状态自主路由到文献、假设、设计、研究实施、数据、分析、解释或传播工作。

## 适合什么时候用

- 从零建立一个可持续迭代的科研项目。
- 接管已有研究目录，重新理解现有数据、分析、文献和结论。
- 只给出科研目标，让 Agent 自主判断下一条信息增益最高的工作。
- 需要长期保留 Design freeze、Study deviation、Analysis provenance、Claim boundary 和 Git 历史。

## 使用方式

这是一个用户显式启动的 Skill。通常只需要调用 `akira-research` 并给出项目路径与研究目标；后续子工作流由 Router 自主选择。项目用 `RESEARCH.md` 保存短小的当前状态并作为人类科研首页，用 `.research/research.sqlite` 保存结构化科研 provenance。长期人类科研文件采用稳定格式和项目内相对 Markdown 导航；普通历史由 Git 保存，不通过复制 `v1`、`final`、`latest` 等文件维护版本。

## 关键边界

它不是固定阶段流水线，也不要求每个项目都经过 Hypothesis、Study 或全部子 Skill。只有存在真正的科学需要时才进入对应工作流；当下一条判别性证据必须依赖新样品、新实验、新权限或其他外部现实输入时，应在真实停止边界结束当前循环。

`RESEARCH.md` 的一级标题、二级章节集合与顺序是固定的人类界面；没有内容的必需章节必须明确写不适用、未记录、未知或待确认，而不是删除或留空。导航只指向真实存在的人类可读 artifact；`.research/` 保留为机器 provenance 与内部支持区。冻结的 Hypothesis / Design 等对象不会仅为了后来补导航而改写，后续关系由下游 artifact、可更新索引和 Research Tree 表达。目录级 Objects / Relations 导航索引只承担人类反向发现，不被 Communication completion 当作新的 scientific source；真实科研对象自己的 canonical artifact 仍正常进入科学来源漂移检查。

Communication Product 可以从 `completed` 终止为 `superseded`，用于保留已被新稿替代的历史产品；该 transition 不允许同时改写产品定义或科学 `source_commit`，且 superseded 后不能重新激活。历史传播 artifact 继续保留 provenance，但不再参与当前 completed-product 的科学源漂移检查或当前传播文本的学术语言门禁。中文科研项目仍可合法维护纯英文期刊稿；只有包含中文叙述的传播段落继续执行中文成熟术语检查。

高通量测序（Next-Generation Sequencing, NGS）作为领域执行能力接入现有分层，不新增科研阶段：真实建库和测序实施属于 `study`，测序数据处理属于 `data → ngs`，测序统计/生物信息推断属于 `analysis → ngs`，结果的科学解释仍属于 `interpretation`。

当科研问题和方法已经由 Akira 确定，但缺少某个专业软件、数据库或领域工具的可靠执行知识时，可以按需推荐第三方 Skill。当前 K-Dense Scientific Agent Skills 只作为**按需发现源**：Agent 必须先核验具体 Skill 的来源、revision、license、脚本/网络/凭据和职责重叠，再向用户说明用途并请求许可；用户同意后通过 `akira` Router 自带安装器把所需 Skill 安装到机器级 `~/.agents/skills/`；Lattice 根安装器不会预装这些外部能力。具体执行器如何加载该机器级 Skill 由执行器自己负责。外部 Skill 只负责工具实现，不能反过来决定 Research Question、Design、Analysis scientific intent 或 scientific Claim。

# design

`design` 负责把 Research Question 或 Hypothesis 转成可执行的 Research Design，包括 estimand、独立推断单位、sampling、comparison、measurement、controls、missingness、QC、bias protection 和结果前停止规则。

Design 表示“计划做什么”，不是实际发生了什么。进入真实研究实施后，偏离、失败样本和实际 Assay 情况由 `study` 记录，不能为了匹配结果回写已经冻结的 Design。

Akira 的 Git / `research.sqlite` 结果前 freeze 只是项目内部的时间与版本 provenance，不等于外部 preregistration、trial registration、systematic-review protocol registration 或 Registered Report Stage 1 acceptance。对外声称“已预注册 / 已注册”必须有真实 registry / journal artifact、identifier 与登记时序；模板、内部 Design、Git freeze 或“计划注册”都不能当作完成注册的证据。

长期人类 Design 固定写入 `designs/<slug>.md`，目录索引为 `designs/README.md`。正文使用固定 H1/H2 与 Navigation；某项不适用时显式写明原因而不是删除章节。目录索引固定包含 `Objects` 与 `Relations`，并用相对链接暴露已知的上游 Hypothesis 与下游 Study / Analysis。首次进入 frozen / execution-ready 前，`research-db` 会先机械核验固定路径、章节顺序和已知上游导航，再执行学术语言检查；检查失败不会写入 frozen / execution-ready。Design 冻结后不为后来产生的 Study、Dataset 或 Analysis 回写下游链接，反向发现由可更新索引与 Research Tree 承担。

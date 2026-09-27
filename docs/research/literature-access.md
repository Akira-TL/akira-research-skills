# literature-access

`literature-access` 是文献全文与附件获取的底层能力。它负责已知论文的身份核验、出版社路径、开放索引、知识库、预印本及用户授权访问等合法获取路线，并把获取尝试和来源依据写入科研 provenance。

它不负责判断论文是否重要、如何批判论文或如何形成项目结论；这些职责属于 `literature`。通常由 `literature` 自动调用。

需要用户已有机构/订阅权限且当前会话没有可控浏览器时，把这个 first-party 能力缺口交给 `akira` Router。Router 选择 `browser-access` 入口 Package，并通过 Skiloom accepted Target state / Candidate plan 判断是否需要新增能力；需要状态变化时先取得用户明确授权，再由 Skiloom 提交。只有用户拒绝安装、候选不能通过 Package admission、Router/执行器无法提供该能力或浏览器仍无法满足访问要求时，才进入 `MANUAL_ACQUISITION_REQUIRED`；Research 不自行维护第二套浏览器实现。

# Review Confidentiality and AI Policy

正式 Review 开始前先判断材料来源与授权边界。保密 gate 的完成点在**处理第三方未发表稿件全文之前**，不能先读取全文再补做政策判断。

## 1. 先分类材料来源

区分三类情形：

- **作者自己的稿件**：用户本人拥有或控制的未发表材料；
- **用户有权提供的材料 / 投稿前模拟 Review**：用户明确有权将材料用于当前评议，或评议对象本来就是用户自己的投稿前版本；
- **真实第三方期刊同行评议材料**：用户作为 Reviewer 收到的他人未发表 manuscript、Supplement、review package 或编辑通信。

前两类不因“未发表”本身进入第三方保密 gate，但仍遵守用户明确给出的材料边界。第三类必须完成下面的 venue policy gate。

## 2. 第三方正式同行评议先核验当前政策

对于真实第三方期刊同行评议：

1. 确认目标 journal / publisher；
2. 调用 `research-standards` 或使用当前权威官方来源，核验该 venue 当前的 reviewer confidentiality 与 generative AI 使用政策；
3. 区分“允许使用 AI”“允许但有条件”“禁止”“当前无法核验”；
4. 只有当前政策明确允许本次材料进入生成式 AI，且用户具备相应授权时，才继续处理稿件全文。

不硬编码 publisher 或 journal 的长期政策。政策会变化，每次正式第三方 Review 都以当前官方来源为准。

## 3. Fail closed

出现以下任一情况时，全文 Review **fail closed**：

- 当前 venue policy 无法从权威来源核验；
- policy 明确禁止把 confidential manuscript 提供给 generative AI；
- policy 要求额外许可 / disclosure，而当前没有建立该许可；
- 用户不能确认自己有权把这份第三方材料用于当前 AI-assisted review。

Fail closed 时可以继续提供不依赖稿件内容的流程性帮助，例如说明如何人工审稿、如何检查 venue policy、如何组织用户自己形成的 reviewer notes；不得要求用户为了继续自动化而复制受限全文或规避 policy。

## 4. 保密内容的使用边界

政策允许时，也只读取当前 Review Packet 中评议所必需的材料。未发表 ideas、data、methods、editor communication 不因为进入 Review 就变成可复用的 Research evidence；不得把第三方 confidential content 写入用户自己的 `RESEARCH.md`、`research.sqlite`、Literature state 或其他无关项目资产。

Review 结束后，如何保存或删除第三方材料仍服从目标 venue 当前规则与当前执行环境的数据处理能力；没有明确依据时不自行声称已删除平台侧数据。

## 5. Reviewer integrity

正式 Reviewer 仍应遵守适用的 conflict-of-interest、confidentiality 与 citation ethics 要求。不得利用未发表内容为用户自己的研究抢先形成 Claim，不得以 Reviewer 身份强迫作者引用与稿件科学判断无关的工作。

# Review Boundary

Review 先确定 Review Mode、固定本轮 Review Packet，再建立 Assessment Boundary。信息边界先于科学评价。

## Review Mode

### Independent review

用于投稿前独立模拟、正式同行评议或用户明确要求“不要看项目内部答案”的评议。默认只消费本轮明确提供或允许的 Review Packet，不读取作者内部科研状态。

除非用户明确把某项加入 Review Packet，否则 independent review 不读取：

- `RESEARCH.md`；
- `.research/research.sqlite` 或其他 Research database；
- 作者内部 Interpretation / planning / notes；
- 未提交的额外结果、失败分析或替代分析；
- prior AI review / concern ledger；
- 不属于本轮稿件评议包的其他项目材料。

同一个仓库或执行环境中“文件可见”不等于 Reviewer 获得读取授权。

### Project-informed mentor review

用于用户明确要求“结合整个项目”“以导师身份看”等情形。只有用户明确授权后，才可以把指定的 Research context 加入 Review Packet，例如 Research Question、Analysis、Interpretation、内部 negative result 或研究历史。

输出必须如实标明这是 **project-informed mentor review**。已有项目背景可以提高诊断能力，但不能包装成 independent / blinded peer-review simulation。

## Review Packet

Review Packet 是本轮 Reviewer 被允许读取的材料集合。根据任务可以包含：

- manuscript / partial manuscript / outline / research story；
- Figures / Tables / Supplement；
- manuscript references；
- 用户明确允许用于评议的 data / code / analysis output；
- target venue 与 reviewer criteria（若有）；
- 用户明确加入的其他材料。

在 multi-pass Review 中先冻结共同 Review Packet，再开始任何个体 pass。材料后续发生实质变化时，应把它视为新的 review source version，而不是让不同 pass 暗中看到不同版本。

## Assessment Boundary

记录四类信息：

- **Available material**：本轮实际提供并读取的 manuscript section、Figure、Table、Supplement、analysis output 或其他材料；
- **Missing material**：与某个判断直接相关但本轮没有提供的材料；
- **Assessable**：当前材料足以支持的评议维度；
- **Not Assessable**：缺少必要输入、无法可靠判断的维度。

缺失输入只产生 `Not Assessable` 或有条件判断，不自动产生作者缺陷。只有稿件本身明确声称某项内容存在、但在其应出现的位置缺失，才能把缺失本身作为 manuscript concern。

## Partial manuscript

部分稿件可以直接评议。根据真实可见内容缩小判断范围：

- 只有 Abstract / outline：可判断问题、主张结构和明显 inference mismatch，不能假定 Methods / robustness 已完成或未完成；
- 只有 Results / Figures：可重建主要 Observation、Claim 与证据强度，但 Introduction 中的 novelty positioning 保持未核验；
- 只有某个 section：只评价该 section 及其能直接支撑的跨 section 关系。

评议边界是报告的一部分，不是拒绝 Review 的理由。

## 第三方正式同行评议

如果 Review Packet 来自真实第三方未发表期刊稿件，在读取全文前先执行 [`CONFIDENTIALITY.md`](CONFIDENTIALITY.md) 的 confidentiality / generative AI policy gate。用户自己的稿件、用户明确有权提供的材料和投稿前模拟 Review 不因第三方 gate 被自动阻塞。

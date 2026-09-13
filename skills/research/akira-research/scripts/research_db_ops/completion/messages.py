from __future__ import annotations

from typing import Any

def append_literature_errors(errors: list[str], blockers: list[dict[str, Any]]) -> None:
    for blocker in blockers:
        reason = str(blocker.get("reason", "unknown"))
        if reason == "relevant_acquired_not_fully_reviewed":
            errors.append(
                f"相关已获取论文 {blocker.get('paper_id')} 尚未完成 Reconstruction + Critical Audit。"
            )
        elif reason == "targeted_paper_not_fully_reviewed":
            errors.append(
                f"定向直接入库论文 {blocker.get('paper_id')} 处于 active/acquired 状态，但尚未完成 Reconstruction + Critical Audit。"
            )
        elif reason == "core_acquired_not_deep_extraction":
            errors.append(
                f"core + acquired 论文 {blocker.get('paper_id')} 未完成 DEEP_EXTRACTION Reconstruction。"
            )
        elif reason == "acquired_candidate_missing_main_text_access_attempt":
            errors.append(
                f"相关已获取 Candidate {blocker.get('candidate_id')} 缺少可审计的正文获取记录。"
            )
        elif reason == "acquired_paper_missing_main_text_access_attempt":
            errors.append(
                f"定向直接入库论文 {blocker.get('paper_id')} 缺少可审计的正文获取记录。"
            )
        elif reason == "acquired_main_text_access_basis_unverified":
            identity = (
                f"Candidate {blocker.get('candidate_id')}"
                if blocker.get("candidate_id") is not None
                else f"Paper {blocker.get('paper_id')}"
            )
            errors.append(
                f"{identity} 的正文来源依据未核验；来源不明的网络镜像不能闭合为正式全文。"
            )
        elif reason == "acquired_main_text_access_basis_detail_missing":
            identity = (
                f"Candidate {blocker.get('candidate_id')}"
                if blocker.get("candidate_id") is not None
                else f"Paper {blocker.get('paper_id')}"
            )
            errors.append(f"{identity} 的正文获取记录缺少来源依据说明。")
        elif reason == "cross_paper_scientific_relation_missing":
            errors.append(
                "主题型 Literature Discovery 已有多篇完成审阅的论文，但 canonical relation graph "
                "缺少跨论文 scientific relation；SHARES_*/CITES 不能替代 Evidence Synthesis 关系。"
            )
        elif reason == "human_literature_unexpected_top_level":
            errors.append(
                f"literature/ 是固定的人类阅读区，不允许临时新增顶层目录或文件：{blocker.get('path')}。"
                "只使用 literature/papers/、literature/collections/ 与 literature/README.md；阅读状态由数据库和用户确认记录表达，不再通过移动文件表示。"
            )
        elif reason == "human_literature_non_readable_file":
            errors.append(
                f"人类文献阅读区出现非 Markdown/PDF 文件：{blocker.get('path')}。"
                "XML/HTML、表格、JSON 与其他机器 artifact 应保存在 .research/artifacts/papers/<paper-id>/。"
            )
        elif reason == "human_literature_nested_directory":
            errors.append(
                f"人类文献阅读区应保持平铺的“题名 - 第一作者 - 年份”文件：{blocker.get('path')}。"
            )
        elif reason == "human_literature_pdf_without_note":
            errors.append(
                f"人类阅读区中的 PDF 缺少同名 Markdown 阅读入口：{blocker.get('path')}。"
            )
        elif reason == "human_literature_confirmation_controls_missing":
            errors.append(
                f"人类阅读 Markdown 缺少顶部/底部标准“我已阅读并确认当前版本”复选框：{blocker.get('path')}。"
            )
        elif reason == "human_literature_unregistered_legacy_file":
            errors.append(
                f"legacy literature/papers/ 中存在未登记到 research.sqlite 的游离文件：{blocker.get('path')}。"
            )
        elif reason == "human_literature_note_structure_invalid":
            errors.append(
                f"人类论文阅读 Markdown 不符合固定 Literature note 结构：{blocker.get('path')}；{blocker.get('detail')}"
            )
        elif reason == "human_literature_versioned_marker":
            errors.append(
                f"人类论文阅读 Markdown 仍使用历史版本型格式 marker：{blocker.get('path')}；请运行 migration 转换为类型标记。"
            )
        elif reason == "human_literature_note_legacy_format":
            errors.append(
                f"人类论文阅读 Markdown 仍是未迁移旧格式：{blocker.get('path')}；新建或迁移后修改的 note 必须采用当前固定格式。"
            )
        elif reason == "human_literature_filename_invalid":
            errors.append(
                f"人类论文文件名不符合“论文题名 - 第一作者 - 年份”并与 metadata 对齐：{blocker.get('path')}。"
            )
        elif reason == "human_literature_pdf_link_invalid":
            errors.append(
                f"人类论文 Markdown 的本地 PDF 链接必须指向存在的同名 PDF：{blocker.get('path')} → {blocker.get('target')}。"
            )
        elif reason == "human_literature_readme_missing":
            errors.append("存在 literature/ 人类阅读区但缺少固定入口 literature/README.md。")
        elif reason == "human_literature_readme_structure_invalid":
            errors.append(
                f"Literature 总索引不符合固定 Navigation/Papers/Collections 结构：{blocker.get('path')}。"
            )
        elif reason == "human_literature_readme_navigation_missing":
            errors.append(
                f"Literature 总索引缺少项目 Research 导航：{blocker.get('path')} → {blocker.get('target')}。"
            )
        elif reason == "human_literature_readme_missing_link":
            errors.append(
                f"Literature 总索引没有覆盖全部论文 note / collection：{blocker.get('path')}；缺少 "
                + ", ".join(str(value) for value in blocker.get("targets", []))
            )
        elif reason == "human_literature_collection_structure_invalid":
            errors.append(
                f"Literature collection 不符合固定 Navigation/Purpose/Papers 结构：{blocker.get('path')}。"
            )
        elif reason == "human_literature_collection_navigation_missing":
            errors.append(
                f"Literature collection 缺少固定人类导航：{blocker.get('path')} → {blocker.get('target')}。"
            )
        elif reason == "human_literature_collection_nonpaper_link":
            errors.append(
                f"Literature collection 的 Papers 只能链接 human paper note：{blocker.get('path')} → {blocker.get('target')}。"
            )
        elif reason == "human_literature_legacy_baseline_invalid":
            errors.append(
                "Literature 人类格式迁移基线无效；不能据此豁免旧 note。"
                f" baseline={blocker.get('baseline_commit')}；{blocker.get('detail')}"
            )
        elif reason == "database_missing":
            errors.append("research.sqlite 不存在；不能完成 Literature completion gate。")

def append_human_artifact_errors(errors: list[str], blockers: list[dict[str, Any]]) -> None:
    for blocker in blockers:
        reason = str(blocker.get("reason", "unknown"))
        path = str(blocker.get("path", "human artifact"))
        if reason == "human_artifact_path_invalid":
            errors.append(
                f"人类科研 artifact 路径不符合 owner 固定格式：{path}；应为 {blocker.get('expected')}。"
            )
        elif reason == "human_artifact_missing_file":
            errors.append(f"已登记的人类科研 artifact 不存在：{path}。")
        elif reason == "human_artifact_upstream_link_missing":
            errors.append(
                f"人类科研 artifact 缺少已知上游导航：{path} → {blocker.get('target')}。"
            )
        elif reason == "human_index_missing_file":
            errors.append(f"存在长期科研对象但缺少目录人类索引：{path}。")
        elif reason == "human_index_missing_object_link":
            errors.append(
                f"目录人类索引没有覆盖全部 canonical 对象：{path}；缺少 "
                + ", ".join(str(value) for value in blocker.get("targets", []))
            )
        elif reason == "human_index_missing_relation_link":
            errors.append(
                f"目录人类索引没有暴露已知科研对象关系：{path}；Relations 缺少 "
                + ", ".join(str(value) for value in blocker.get("targets", []))
            )
        elif reason == "interpretation_human_path_nested":
            errors.append(
                "Interpretation 人类 artifact 必须保持 interpretation/<slug>.md 平铺结构："
                + ", ".join(str(value) for value in blocker.get("paths", []))
            )
        elif reason == "interpretation_upstream_link_missing":
            errors.append(f"Interpretation artifact 缺少 Research 首页之外的真实上游人类入口：{path}。")
        elif reason == "human_markdown_h1_invalid":
            errors.append(f"人类科研 Markdown 的一级标题不符合 owner 格式：{path}。")
        elif reason == "human_markdown_section_order_invalid":
            errors.append(f"人类科研 Markdown 的二级章节集合或顺序不符合 owner 格式：{path}。")
        elif reason == "human_markdown_empty_sections":
            errors.append(
                f"人类科研 Markdown 存在空的必需章节：{path}（"
                + ", ".join(str(value) for value in blocker.get("sections", []))
                + "）。"
            )
        elif reason == "human_markdown_versioned_marker":
            errors.append(f"人类科研 Markdown 不得使用 v1/v2 等格式版本 marker：{path}。")
        elif reason == "human_artifact_legacy_baseline_invalid":
            errors.append(
                "人类科研格式迁移基线无效；不能据此豁免旧格式。"
                f" baseline={blocker.get('baseline_commit')}；{blocker.get('detail')}"
            )
        elif reason in {
            "human_markdown_link_absolute",
            "human_markdown_link_outside_project",
            "human_markdown_link_internal",
            "human_markdown_link_missing",
        }:
            errors.append(
                f"人类科研 Markdown 导航链接无效或越过人类/机器边界：{path} → {blocker.get('target')}。"
            )
        elif reason == "database_missing":
            errors.append("research.sqlite 不存在；不能校验核心人类科研 artifact。")


def append_downstream_errors(errors: list[str], blockers: list[dict[str, Any]]) -> None:
    for blocker in blockers:
        reason = str(blocker.get("reason", "unknown"))
        if reason == "tracked_downstream_artifacts_unregistered":
            errors.append(
                "data/analysis 下存在已被 Git 跟踪但未登记到 research.sqlite 的科研 artifact："
                + ", ".join(str(path) for path in blocker.get("paths", []))
            )
        elif reason == "data_assets_present_without_dataset_record":
            errors.append("项目存在 data/ 科研资产，但 research.sqlite 尚未登记 Dataset。")
        elif reason == "analysis_assets_present_without_analysis_record":
            errors.append("项目存在 analysis/ 科研资产，但 research.sqlite 尚未登记 Analysis Run。")
        elif reason == "completed_analysis_missing_dataset_input":
            errors.append(f"已完成 Analysis {blocker.get('analysis')} 没有关联输入 Dataset。")
        elif reason == "completed_analysis_missing_estimate_artifact":
            errors.append(f"已完成 Analysis {blocker.get('analysis')} 没有登记主要 estimate artifact。")
        elif reason == "completed_analysis_missing_project_observation":
            errors.append(f"已完成 Analysis {blocker.get('analysis')} 没有登记项目自身 Observation。")
        elif reason == "completed_analysis_missing_selected_attempt":
            errors.append(
                f"已完成 Analysis {blocker.get('analysis')} 没有且仅有一个 selected Analysis Attempt；"
                f"当前 selected 数量为 {blocker.get('selected_attempt_count')}。"
            )
        elif reason == "selected_analysis_attempt_missing_commit":
            errors.append(
                f"Analysis {blocker.get('analysis')} 的 selected Attempt {blocker.get('attempt')} 缺少 Git commit。"
            )
        elif reason == "analysis_timestamp_invalid":
            errors.append(f"Analysis {blocker.get('analysis')} 的 started_at/completed_at/updated_at 时间戳无效。")
        elif reason == "analysis_completed_before_started":
            errors.append(f"Analysis {blocker.get('analysis')} 的 completed_at 早于 started_at。")
        elif reason == "analysis_completed_after_last_update":
            errors.append(
                f"Analysis {blocker.get('analysis')} 的 completed_at 晚于最后一次数据库 updated_at；"
                "完成时间不能指向尚未发生的未来时刻。"
            )
        elif reason == "confirmatory_analysis_missing_freeze_commit":
            errors.append(f"确认性 Analysis {blocker.get('analysis')} 缺少结果可见前 freeze commit。")
        elif reason == "analysis_freeze_commit_missing":
            errors.append(
                f"Analysis {blocker.get('analysis')} 记录的 freeze commit 不存在：{blocker.get('freeze_commit')}。"
            )
        elif reason == "analysis_freeze_commit_not_ancestor":
            errors.append(
                f"Analysis {blocker.get('analysis')} 的 freeze commit 不是当前 HEAD 的祖先：{blocker.get('freeze_commit')}。"
            )
        elif reason == "confirmatory_analysis_design_link_missing":
            errors.append(
                f"确认性 Analysis {blocker.get('analysis')} 与已登记 Research Design 匹配，但缺少结构化 design link："
                + ", ".join(str(value) for value in blocker.get("matching_designs", []))
            )
        elif reason == "analysis_design_missing":
            errors.append(
                f"Analysis {blocker.get('analysis')} 引用的 Research Design 不存在：{blocker.get('design_id')}。"
            )
        elif reason == "confirmatory_analysis_design_not_frozen":
            errors.append(
                f"确认性 Analysis {blocker.get('analysis')} 引用的 Research Design {blocker.get('design')} 尚未冻结。"
            )
        elif reason == "design_freeze_after_analysis_freeze":
            errors.append(
                f"Analysis {blocker.get('analysis')} 的结果前 freeze 早于 Research Design {blocker.get('design')} 的 freeze；"
                "确认性分析不能先于其设计冻结。"
            )
        elif reason == "analysis_plan_or_input_missing_at_freeze":
            errors.append(
                f"Analysis {blocker.get('analysis')} 的 freeze commit 未冻结全部主要计划/代码/输入："
                + ", ".join(str(path) for path in blocker.get("paths", []))
            )
        elif reason == "analysis_frozen_artifact_changed_after_freeze":
            errors.append(
                f"Analysis {blocker.get('analysis')} 的已冻结计划/代码/输入在 freeze 后发生提交内容变化："
                + ", ".join(str(path) for path in blocker.get("paths", []))
                + "；请保留冻结版本，并把结果后修订作为新增 artifact/amendment。"
            )
        elif reason == "analysis_post_result_context_present_at_freeze":
            errors.append(
                f"Analysis {blocker.get('analysis')} 把 freeze 时已存在的 Dataset artifact 标成 post_result_context："
                + ", ".join(str(path) for path in blocker.get("paths", []))
                + "；post_result_context 只用于结果可见后新增、未参与该执行快照的 provenance/context artifact。"
            )
        elif reason == "analysis_post_result_context_predates_results":
            errors.append(
                f"Analysis {blocker.get('analysis')} 的 post_result_context 早于任何已登记 result artifact 进入 Git 历史："
                + ", ".join(str(path) for path in blocker.get("paths", []))
                + "；无法机械证明该 context 是结果可见后才形成的。"
            )
        elif reason == "analysis_result_artifact_present_at_freeze":
            errors.append(
                f"Analysis {blocker.get('analysis')} 的结果 artifact 已存在于所声明的 pre-result freeze："
                + ", ".join(str(path) for path in blocker.get("paths", []))
            )
        elif reason == "downstream_schema_missing":
            errors.append(
                "下游科研 provenance schema 尚未迁移完成："
                + ", ".join(str(name) for name in blocker.get("tables", []))
            )

def append_planning_errors(errors: list[str], blockers: list[dict[str, Any]]) -> None:
    for blocker in blockers:
        reason = str(blocker.get("reason", "unknown"))
        if reason == "hypothesis_artifacts_unregistered":
            errors.append(
                "hypotheses/ 下存在尚未登记到 research.sqlite 的 canonical Hypothesis Set artifact："
                + ", ".join(str(path) for path in blocker.get("paths", []))
            )
        elif reason == "design_artifacts_unregistered":
            errors.append(
                "designs/ 下存在尚未登记到 research.sqlite 的 canonical Research Design artifact："
                + ", ".join(str(path) for path in blocker.get("paths", []))
            )
        elif reason in {"hypothesis_freeze_commit_missing", "hypothesis_freeze_commit_not_found"}:
            errors.append(
                f"Hypothesis Set {blocker.get('hypothesis_set')} 缺少有效 freeze commit：{blocker.get('freeze_commit')}。"
            )
        elif reason == "hypothesis_freeze_commit_not_ancestor":
            errors.append(
                f"Hypothesis Set {blocker.get('hypothesis_set')} 的 freeze commit 不是当前 HEAD 的祖先。"
            )
        elif reason == "hypothesis_artifact_missing_at_freeze":
            errors.append(
                f"Hypothesis Set {blocker.get('hypothesis_set')} 的 canonical artifact 在所声明 freeze commit 中不存在："
                f"{blocker.get('path')}"
            )
        elif reason == "hypothesis_set_missing_proposal_provenance":
            errors.append(
                f"Hypothesis Set {blocker.get('hypothesis_set')} 是 schema v18 provenance 启用后新建的集合，"
                "但没有链接任何 Hypothesis Proposal。"
            )
        elif reason in {"design_freeze_commit_missing", "design_freeze_commit_not_found"}:
            errors.append(
                f"Research Design {blocker.get('design')} 缺少有效 freeze commit：{blocker.get('freeze_commit')}。"
            )
        elif reason == "design_freeze_commit_not_ancestor":
            errors.append(
                f"Research Design {blocker.get('design')} 的 freeze commit 不是当前 HEAD 的祖先。"
            )
        elif reason == "design_or_hypothesis_missing_at_freeze":
            errors.append(
                f"Research Design {blocker.get('design')} 的 freeze commit 未同时冻结 Design 与关联 Hypothesis Set："
                + ", ".join(str(path) for path in blocker.get("paths", []))
            )
        elif reason == "linked_hypothesis_missing_freeze":
            errors.append(
                f"Research Design {blocker.get('design')} 已冻结，但关联 Hypothesis Set "
                f"{blocker.get('hypothesis_set')} 没有可审计 freeze commit。"
            )
        elif reason == "hypothesis_freeze_after_design_freeze":
            errors.append(
                f"Research Design {blocker.get('design')} 的 freeze 早于关联 Hypothesis Set "
                f"{blocker.get('hypothesis_set')} 的 freeze；设计不能先于其判别假设冻结。"
            )
        elif reason == "completed_confirmatory_analysis_missing_hypothesis_evaluation":
            errors.append(
                f"确认性 Analysis {blocker.get('analysis')} 已完成并实现 Research Design {blocker.get('design')}，"
                f"但尚未记录对 Hypothesis Set {blocker.get('hypothesis_set')} 的结果后 Evaluation。"
            )
        elif reason == "hypothesis_evaluation_timestamp_invalid":
            errors.append(
                f"Hypothesis Evaluation 的时间戳无效：Analysis {blocker.get('analysis')}，"
                f"Hypothesis Set {blocker.get('hypothesis_set')}。"
            )
        elif reason == "hypothesis_evaluation_before_analysis_completion":
            errors.append(
                f"Hypothesis Evaluation 早于其所引用 Analysis {blocker.get('analysis')} 的 completed_at："
                f"evaluated_at={blocker.get('evaluated_at')}，completed_at={blocker.get('completed_at')}。"
            )
        elif reason == "planning_schema_missing":
            errors.append(
                "Hypothesis/Design provenance schema 尚未迁移完成："
                + ", ".join(str(name) for name in blocker.get("tables", []))
            )

def append_research_tree_errors(errors: list[str], blockers: list[dict[str, Any]]) -> None:
    for blocker in blockers:
        reason = str(blocker.get("reason", "unknown"))
        if reason == "research_tree_schema_missing":
            errors.append(
                "Research Tree provenance schema 尚未迁移完成："
                + ", ".join(str(name) for name in blocker.get("tables", []))
            )
        elif reason == "research_tree_state_missing":
            errors.append("Research Tree 已存在 Node，但尚未设置 root/active path。")
        elif reason == "research_tree_state_without_nodes":
            errors.append("Research Tree state 已存在，但项目没有任何 Research Node。")
        elif reason in {"research_tree_state_dangling", "research_tree_parent_chain_dangling"}:
            errors.append("Research Tree state 或 parent chain 引用了不存在的 Research Node。")
        elif reason == "research_tree_root_has_parent":
            errors.append(f"Research Tree root {blocker.get('root')} 仍有 parent；root 必须是结构根节点。")
        elif reason == "research_tree_active_node_inactive":
            errors.append(
                f"Research Tree active node {blocker.get('active')} 已处于 {blocker.get('status')}；"
                "active path 必须指向仍可推进的 open/active/blocked 节点。"
            )
        elif reason == "research_tree_parent_cycle":
            errors.append("Research Tree parent chain 出现 cycle。")
        elif reason == "research_tree_active_outside_root":
            errors.append(
                f"Research Tree active node {blocker.get('active')} 不位于 root {blocker.get('root')} 的结构子树中。"
            )
        elif reason == "research_tree_closed_without_reason":
            errors.append(f"Research Node {blocker.get('node')} 已关闭但缺少 closure_reason。")
        elif reason == "research_tree_view_missing":
            errors.append("Research Tree 已有科研节点，但缺少 research-tree/README.md 人类总图。")
        elif reason == "research_tree_view_missing_node":
            errors.append("Research Tree 人类总图缺少 canonical Node。")
        elif reason == "research_tree_view_extra_node":
            errors.append("Research Tree 人类总图出现数据库中不存在的 Node。")
        elif reason == "research_tree_view_missing_edge":
            errors.append("Research Tree 人类总图缺少 canonical parent/scientific edge。")
        elif reason == "research_tree_view_extra_edge":
            errors.append("Research Tree 人类总图出现无 canonical relation 支持的 edge。")
        elif reason == "research_tree_view_mermaid_block_invalid":
            errors.append("Research Tree 人类视图必须且只能包含一张 Mermaid 总图。")
        elif reason == "research_git_branch_name_invalid":
            errors.append(
                f"Research Node {blocker.get('node')} 的 Git branch 命名不符合科研分支规范："
                f"{blocker.get('branch')}；应为 {blocker.get('expected')}。"
            )
        elif reason == "research_git_commit_missing":
            errors.append(
                f"Research Node {blocker.get('node')} 的 Git branch provenance 引用了不存在的 base/tip commit。"
            )
        elif reason == "research_git_base_not_ancestor":
            errors.append(
                f"Research Node {blocker.get('node')} 的已登记 base commit 不是当前 tip 的祖先；"
                "科研 branch 历史可能被重写。"
            )
        elif reason == "research_git_active_branch_out_of_sync":
            errors.append(
                f"Research Node {blocker.get('node')} 的 active Git branch 与数据库 tip 不一致："
                f"{blocker.get('branch')}。完成前先同步 branch provenance。"
            )
        elif reason == "research_git_merged_tip_not_in_main":
            errors.append(
                f"Research Node {blocker.get('node')} 标记为 merged，但已登记 branch tip 尚未进入 main。"
            )
        elif reason == "research_git_archive_ref_invalid":
            errors.append(
                f"Research Node {blocker.get('node')} 的归档 ref 不符合 research-closed/<kind>/<slug>："
                f"应为 {blocker.get('expected')}。"
            )
        elif reason == "research_git_archive_tag_mismatch":
            errors.append(
                f"Research Node {blocker.get('node')} 的 archival tag {blocker.get('tag')} 不存在或没有固定已登记 tip。"
            )


def append_study_errors(errors: list[str], blockers: list[dict[str, Any]]) -> None:
    for blocker in blockers:
        reason = str(blocker.get("reason", "unknown"))
        if reason == "study_schema_missing":
            errors.append(
                "Study provenance schema 尚未迁移完成："
                + ", ".join(str(name) for name in blocker.get("tables", []))
            )
        elif reason == "study_design_missing":
            errors.append(f"Study {blocker.get('study')} 引用的 Research Design 不存在。")
        elif reason == "study_design_not_frozen":
            errors.append(
                f"Study {blocker.get('study')} 引用的 Research Design {blocker.get('design')} 尚未冻结。"
            )
        elif reason == "study_timestamp_invalid":
            errors.append(f"Study {blocker.get('study')} 的时间戳无效。")
        elif reason == "study_started_after_last_update":
            errors.append(f"Study {blocker.get('study')} 的 started_at 晚于数据库 updated_at。")
        elif reason == "study_completed_before_started":
            errors.append(f"Study {blocker.get('study')} 的 completed_at 早于 started_at。")
        elif reason == "study_completed_after_last_update":
            errors.append(f"Study {blocker.get('study')} 的 completed_at 晚于数据库 updated_at。")
        elif reason == "completed_study_missing_completed_at":
            errors.append(f"已完成 Study {blocker.get('study')} 缺少 completed_at。")
        elif reason == "completed_study_has_active_assays":
            errors.append(
                f"已完成 Study {blocker.get('study')} 仍有未结束 Assay："
                + ", ".join(str(value) for value in blocker.get("assays", []))
            )


def append_communication_errors(errors: list[str], blockers: list[dict[str, Any]]) -> None:
    for blocker in blockers:
        reason = str(blocker.get("reason", "unknown"))
        if reason == "communication_artifacts_unregistered":
            errors.append(
                "communication/ 或 .research/communication/ 下存在未登记到 research.sqlite 的传播 artifact："
                + ", ".join(str(path) for path in blocker.get("paths", []))
            )
        elif reason == "communication_human_view_unexpected_top_level":
            errors.append(
                f"communication/ 是人类传播入口，除可选 README.md 外顶层只放 Communication Product 目录：{blocker.get('path')}。"
            )
        elif reason == "communication_internal_support_unexpected_top_level":
            errors.append(
                f".research/communication/ 顶层只放 Communication Product 目录，内部支持文件应进入对应 product slug：{blocker.get('path')}。"
            )
        elif reason == "communication_artifact_product_mismatch":
            errors.append(
                f"Communication Product {blocker.get('communication')} 的 artifact 位于其他 product workspace：{blocker.get('path')}。"
            )
        elif reason == "communication_derived_output_outside_workspace":
            errors.append(
                f"Communication Product {blocker.get('communication')} 的非 generator 派生传播 artifact 不在 communication/<product-slug>/ 或 .research/communication/<product-slug>/：{blocker.get('path')}。"
            )
        elif reason == "communication_assets_present_without_product_record":
            errors.append(
                "项目存在 communication/ 或 .research/communication/ 传播产物，但 research.sqlite 尚未登记 Communication Product。"
            )
        elif reason in {"communication_source_commit_missing", "communication_source_commit_not_found"}:
            errors.append(
                f"Communication Product {blocker.get('communication')} 缺少有效的 pre-communication source commit。"
            )
        elif reason == "communication_source_commit_not_ancestor":
            errors.append(
                f"Communication Product {blocker.get('communication')} 的 source commit 不是当前 HEAD 的祖先。"
            )
        elif reason == "communication_artifact_timing_mismatch":
            errors.append(
                f"Communication Product {blocker.get('communication')} 的 artifact 与 pre-communication source commit 时序不一致："
                + ", ".join(str(path) for path in blocker.get("paths", []))
            )
        elif reason == "scientific_source_changed_after_communication_freeze":
            errors.append(
                f"Communication Product {blocker.get('communication')} 所依据的科研 source commit 之后仍有科学 canonical artifact 变化；"
                "传播稿必须基于最新稳定证据重新审阅："
                + ", ".join(str(path) for path in blocker.get("paths", []))
            )
        elif reason in {
            "communication_target_workspace_identity_mismatch",
            "communication_target_manifest_identity_mismatch",
        }:
            errors.append(
                f"Communication Product {blocker.get('communication')} 的 target release workspace identity 与已登记 journal code 不一致。"
            )
        elif reason in {
            "communication_target_canonical_source_missing",
            "communication_canonical_source_unregistered",
            "communication_canonical_source_inside_target",
        }:
            errors.append(
                f"Communication Product {blocker.get('communication')} 缺少合法的共享 canonical editable source；target release 不能拥有第二份独立科学稿件。"
            )
        elif reason in {
            "communication_target_source_commit_missing",
            "communication_target_source_commit_not_found",
            "communication_target_source_commit_not_ancestor",
            "communication_target_source_missing_at_commit",
        }:
            errors.append(
                f"Communication Product {blocker.get('communication')} / {blocker.get('journal_code')} 的 target source commit 无效。"
            )
        elif reason == "communication_target_source_drift":
            errors.append(
                f"Communication Product {blocker.get('communication')} / {blocker.get('journal_code')} 的 canonical source 已在 target build 后变化；必须重新 build 并重新登记 target workspace。"
            )
        elif reason in {
            "communication_target_manifest_invalid",
            "communication_target_manifest_file_drift",
        }:
            errors.append(
                f"Communication Product {blocker.get('communication')} / {blocker.get('journal_code')} 的 target manifest 与当前 build source 不一致。"
            )
        elif reason in {
            "communication_target_file_missing",
            "communication_target_file_oid_unavailable",
            "communication_target_build_source_drift",
        }:
            errors.append(
                f"Communication Product {blocker.get('communication')} / {blocker.get('journal_code')} 的 target build source 已缺失或漂移：{blocker.get('path')}。"
            )
        elif reason == "communication_target_generated_output_stored":
            errors.append(
                f"Communication Product {blocker.get('communication')} / {blocker.get('journal_code')} 的 target release source tree 中保存了 DOCX/XLSX/PDF/PPTX 或 manifest 声明的其他生成表示；应修改 source/generator 后重建，而不是把生成文件作为可编辑 authority："
                + ", ".join(str(path) for path in blocker.get("paths", []))
            )
        elif reason == "communication_target_unexpected_file":
            errors.append(
                f"Communication Product {blocker.get('communication')} / {blocker.get('journal_code')} 的 target release workspace 出现 manifest 未声明的额外文件；target workspace 不能保存第二份独立可编辑稿件："
                + ", ".join(str(path) for path in blocker.get("paths", []))
            )
        elif reason == "communication_target_workspace_unregistered":
            errors.append(
                "项目出现 `<journal-code>-release/` 目录但没有登记对应 target journal/workspace："
                + ", ".join(str(path) for path in blocker.get("paths", []))
            )
        elif reason in {
            "communication_release_tag_name_invalid",
            "communication_release_tag_unregistered",
        }:
            errors.append(
                f"Communication Product {blocker.get('communication')} 存在未通过正式 tag gate 建立的稿件 tag 或非法命名：{blocker.get('tag')}。"
            )
        elif reason in {
            "communication_release_tag_missing",
            "communication_release_tag_not_annotated",
            "communication_release_tag_object_changed",
            "communication_release_tag_commit_changed",
        }:
            errors.append(
                f"Communication Product {blocker.get('communication')} 的正式 manuscript tag 已缺失、变为 lightweight 或被移动/重建：{blocker.get('tag')}。正式 tag 一经创建不可改写。"
            )
        elif reason in {
            "communication_release_version_sequence_invalid",
            "communication_release_baseline_approval_missing",
        }:
            errors.append(
                f"Communication Product {blocker.get('communication')} / {blocker.get('journal_code')} 的正式稿件版本序列或整数 baseline 批准依据无效：{blocker.get('version')}。"
            )
        elif reason == "communication_public_release_evidence_invalid":
            errors.append(
                f"Communication Product {blocker.get('communication')} 的公开 release tag 缺少真实日期/evidence，或日期位于未来：{blocker.get('tag')}。"
            )
        elif reason in {
            "communication_release_base_tag_missing",
            "communication_release_commit_mismatch",
        }:
            errors.append(
                f"Communication Product {blocker.get('communication')} 的公开 release tag 没有保持与基础 manuscript checkpoint 同一 commit：{blocker.get('tag')}。"
            )
        elif reason == "completed_communication_missing_artifacts":
            errors.append(f"Communication Product {blocker.get('communication')} 已完成但没有登记传播 artifact。")
        elif reason in {"communication_assets_present_without_database", "communication_schema_missing"}:
            errors.append("Communication provenance schema 尚未迁移完成，但项目已经存在传播产物。")

def append_project_state_errors(errors: list[str], blockers: list[dict[str, Any]]) -> None:
    for blocker in blockers:
        reason = str(blocker.get("reason", "unknown"))
        if reason == "human_markdown_versioned_marker":
            errors.append(
                "RESEARCH.md 的人类格式类型标记不得携带 v1/v2 等格式版本身份："
                + ", ".join(str(marker) for marker in blocker.get("markers", []))
            )
        elif reason == "human_markdown_h1_invalid":
            errors.append("RESEARCH.md 必须且只能有一个 `# Research` 一级标题。")
        elif reason == "human_markdown_section_order_invalid":
            errors.append("RESEARCH.md 的二级章节集合或顺序不符合固定人类可读格式。")
        elif reason == "human_markdown_empty_sections":
            errors.append(
                "RESEARCH.md 的必需章节不能为空；未知、不适用或待确认必须显式写明："
                + ", ".join(str(name) for name in blocker.get("sections", []))
            )
        elif reason == "human_markdown_link_missing":
            errors.append(
                f"RESEARCH.md 的人类导航链接目标不存在：{blocker.get('target')}。"
            )
        elif reason == "human_markdown_link_internal":
            errors.append(
                f"RESEARCH.md 的普通人类导航不能把 .research/ 机器内部状态作为入口：{blocker.get('target')}。"
            )
        elif reason in {"human_markdown_link_absolute", "human_markdown_link_outside_project"}:
            errors.append(
                f"RESEARCH.md 的本地导航必须使用项目内相对路径：{blocker.get('target')}。"
            )
        elif reason == "research_state_missing_file":
            errors.append("项目根目录缺少 RESEARCH.md，不能完成 current research state gate。")
        elif reason == "research_state_missing_sections":
            errors.append(
                "RESEARCH.md 缺少当前科研状态必需 section："
                + ", ".join(str(name) for name in blocker.get("sections", []))
            )
        elif reason == "research_state_invalid_current_loop":
            errors.append(
                "RESEARCH.md 的 Current Loop 不是允许的科研定位词："
                + repr(blocker.get("current_loop"))
            )
        elif reason == "research_state_active_work_empty":
            errors.append(
                "RESEARCH.md 的 Active Work 为空；完成时必须写明下一条真实动作、等待/blocker 或有边界停止状态。"
            )
        elif reason == "research_state_competing_explanation_is_evidence_status":
            errors.append(
                "RESEARCH.md 的 Competing explanations 把证据/工作状态写成了科学竞争解释："
                + ", ".join(str(marker) for marker in blocker.get("markers", []))
                + "。竞争解释必须描述科学对象可能处于的替代状态；证据不足或当前无法判断应写入 Discriminating gap / Current State。"
            )
        elif reason == "research_state_active_work_stale_completion":
            errors.append(
                "RESEARCH.md 的 Active Work 仍描述 Git/validator 收尾动作，说明 current state 尚未在最终提交前刷新："
                + ", ".join(str(marker) for marker in blocker.get("markers", []))
            )


def append_academic_language_errors(errors: list[str], blockers: list[dict[str, Any]]) -> None:
    for blocker in blockers:
        reason = blocker.get("reason")
        if reason in {
            "bare_english_term_in_chinese_communication",
            "bare_english_term_in_chinese_research_text",
        }:
            surface = "中文传播稿" if reason == "bare_english_term_in_chinese_communication" else "中文科研文本"
            errors.append(
                f"{surface}存在已有成熟中文表述却直接裸用的英文术语：{blocker.get('path')} "
                f"第 {blocker.get('paragraph')} 段（{', '.join(blocker.get('terms', []))}）。"
                "首次出现应优先使用规范的“中文标准术语（English term）”，后续使用中文术语或标准缩写。"
            )
        else:
            errors.append(
                f"中文科研项目的人类可读科研文本存在大段英文叙述：{blocker.get('path')} "
                f"第 {blocker.get('paragraph')} 段。应改为规范中文学术表述；英文仅作为标准术语首次出现时的括注或必要书目信息。"
            )

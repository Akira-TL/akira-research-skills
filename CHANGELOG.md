# Changelog

本文件记录 `akira-research-skills` 的用户可见变化。

## Unreleased

### Added

- 建立独立 Research 产品仓，并保留原 Research 系列的主要 Git 历史。
- 增加 `skills/research/`、`docs/research/`、`in-progress` 与 `deprecated` 生命周期目录。
- 增加仓库级 `CONTEXT.md`、`.agents/` 维护约定和统一检查脚本。

### Changed

- Research suite 从通用 Akira Skill 仓拆出，科研项目可以独立安装完整 Research 能力。
- Hypothesis、Design、Study、Dataset、Analysis 与 Interpretation 的长期人类 Markdown 采用 owner-defined 固定格式、相对导航与目录索引；目录索引固定区分 `Objects` / `Relations` 并机械覆盖已知上/下游关系，completion 同时验证路径、H1/H2、已知上游导航和本地链接完整性。
- Hypothesis / Design 首次进入 frozen / execution-ready 前先通过严格人类格式 preflight，再执行学术语言检查；格式错误不会先写入冻结状态，避免 completion 阶段才发现必须回写冻结正文。
- 旧项目升级到严格人类格式契约时记录迁移前 Git baseline；只有契约启用前且迁移后未改动的历史 artifact 可原样保留，一旦迁移后编辑即必须采用当前格式，避免为了排版回写结果前冻结科研正文。
- Literature 人类阅读区采用无格式版本号的 `akira:literature-note` 类型标记，并严格化 `literature/README.md`、Collection、论文文件命名、同名 PDF 与本地导航；迁移只确定性替换历史版本型 marker，更早旧 note 只在真实 Git migration baseline 下保持兼容。

# Canonical install block

Akira Research 作为完整科研产品族项目级安装，不作为全局默认 Skill 集。

## 项目级安装整个 Research suite

```bash
npx skills add Akira-TL/akira-research-skills --skill '*' --agent '*' -y
```

## 查看当前仓库可安装 Skill

```bash
npx skills add Akira-TL/akira-research-skills --list
```

本地维护 checkout 使用：

```bash
npx skills add . --list
```

README、迁移说明和其他安装文档引用安装方式时，以本文件为准。除非用户明确要求，不加 `-g`；浏览器、DOCX/PPT、OpenAI Plugins、K-Dense 等外部能力不随 Research suite 自动安装。

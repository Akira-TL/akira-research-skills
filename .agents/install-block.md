# Akira Research 安装

Akira Research 是完整科研产品族，只在真实科研任务需要时由 `akira` Router 安装到机器级 Skill 注册表；Lattice 根安装器不预装 Research。

## 安装完整 Research suite

```bash
uv run python ~/.agents/skills/akira/scripts/skills.py install \
  https://github.com/Akira-TL/akira-research-skills.git \
  --all \
  --root skills/research
```

安装器从远端 GitHub checkout 到 `~/.agents/sources/`，再把每个 Research Skill 以软链接注册到 `~/.agents/skills/`。Skill 内容不复制。

## 安装前检查远端 Skill

```bash
uv run python ~/.agents/skills/akira/scripts/skills.py inspect \
  https://github.com/Akira-TL/akira-research-skills.git
```

`inspect` 只更新共享 source cache 并列出可发现的 `SKILL.md`，不创建机器级注册项。

## 本地维护 checkout

本地 `skills/research` checkout 只用于开发、review、测试与固定 revision，不作为运行时安装 source。开发时使用仓库自己的：

```bash
./scripts/check.sh
```

具体执行器如何发现、链接或加载已注册的 `~/.agents/skills`，由对应执行器自己负责，不属于 Research 产品安装协议。

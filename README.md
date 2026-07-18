# BITFSAE Skills

BITFSAE 队内共享的 Codex Skills。每个 Skill 都是独立目录，可单独安装、维护和发布；本仓库用于代码审核、版本追踪和代际交接。

## 当前 Skills

| Skill | 用途 | 调用建议 |
| --- | --- | --- |
| [`bitfsae-project-standards`](skills/bitfsae-project-standards/SKILL.md) | 全项目规范审查、文档体系、共享接口、交接与发布治理 | 仅在明确需要全项目工作时调用，不用于普通代码修改、构建或 Git 操作 |

## 目录结构

```text
bitfsae-skills/
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md             # 必需；触发描述和执行规范
│       ├── agents/openai.yaml   # 推荐；界面名称和默认提示
│       ├── references/          # 按需读取的详细规则
│       ├── scripts/             # 可选；需要确定性执行的工具
│       └── assets/              # 可选；交付物模板或素材
├── tools/validate_skills.py
└── .github/
```

一个 Skill 只能依赖自己目录中的资源，不得通过相对路径依赖另一个本地工程。确有共享内容时，应提取成独立 Skill 或在仓库级规则中说明。

## 安装

克隆仓库后，把需要的 Skill 目录复制到 Codex Skills 目录：

```bash
git clone https://github.com/BITFSAE/bitfsae-skills.git
cp -R bitfsae-skills/skills/bitfsae-project-standards ~/.codex/skills/
```

更新时重新同步同名目录，并重新启动或刷新使用 Skills 的客户端。不要把整个仓库根目录当作单个 Skill 安装。

## 参与维护

1. 从最新 `main` 创建分支；
2. 一个 PR 聚焦一个 Skill 或一项仓库基础设施修改；
3. 修改 Skill 时同步检查触发描述、正文、references 和 `agents/openai.yaml`；
4. 执行 `python3 tools/validate_skills.py`；
5. 更新 `CHANGELOG.md`，通过 CI 和维护者审核后 Squash 合并。

详细要求见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 公开仓库边界

不得加入密码、Token、私钥、生产服务器地址、个人信息、未脱敏日志或无权公开的车队/厂家资料。Skill 可以描述凭据应如何管理，但不能包含真实值。

## 许可证

当前尚未确定对外授权方式。在车队确认许可证前，不要加入来源和授权不清楚的第三方 Skill、脚本或模板。

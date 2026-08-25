# BITFSAE Skills

[![skills.sh](https://skills.sh/b/BITFSAE/bitfsae-skills)](https://skills.sh/BITFSAE/bitfsae-skills)

BITFSAE 公开维护、队内共享的 Agent Skills。每个 Skill 都是独立目录，可单独安装、维护和发布；本仓库用于代码审核、版本追踪和代际交接。

## 当前 Skills

| Skill | 用途 | 调用建议 |
| --- | --- | --- |
| [`bitfsae-project-standards`](skills/bitfsae-project-standards/SKILL.md) | 全项目规范审查、文档体系、共享接口、交接与发布治理 | 仅在明确需要全项目工作时调用，不用于普通代码修改、构建或 Git 操作 |
| [`bitfsae-github-workflow`](skills/bitfsae-github-workflow/SKILL.md) | BITFSAE 仓库的分支、提交、PR 审查、协议同步与安全检查 | 在 BITFSAE 仓库处理提交、推送、PR、审查、合并或组织 Git 协作时调用 |

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
├── translations/zh-CN/
│   └── <skill-name>/             # 队内中文镜像；结构对应 skills/
├── tools/validate_skills.py
└── .github/
```

一个 Skill 只能依赖自己目录中的资源，不得通过相对路径依赖另一个本地工程。确有共享内容时，应提取成独立 Skill 或在仓库级规则中说明。

`skills/` 是英文原版和可安装来源；`translations/zh-CN/` 只提供队内中文镜像，不参与 Skills CLI、打包和发布。修改某个 Skill 时必须同步更新对应中文镜像，并保持目录和文件名一致。

## 安装

使用 `skills` CLI 查看仓库中的全部 Skills：

```bash
npx skills add BITFSAE/bitfsae-skills --list
```

把指定 Skill 全局安装到 Codex：

```bash
npx skills add BITFSAE/bitfsae-skills \
  --skill bitfsae-project-standards \
  --agent codex \
  --global

npx skills add BITFSAE/bitfsae-skills \
  --skill bitfsae-github-workflow \
  --agent codex \
  --global
```

也可以克隆仓库后手动安装：

```bash
git clone https://github.com/BITFSAE/bitfsae-skills.git
cp -R bitfsae-skills/skills/bitfsae-project-standards ~/.codex/skills/
cp -R bitfsae-skills/skills/bitfsae-github-workflow ~/.codex/skills/
```

更新时重新同步同名目录，并重新启动或刷新使用 Skills 的客户端。不要把整个仓库根目录当作单个 Skill 安装。

## 发布

### skills.sh

GitHub 是公开发布源，skills.sh 负责发现和展示。Skill 合并并推送到公开仓库后，运行一次安装命令即可让 CLI 发现仓库；页面索引和缓存刷新可能延迟。仓库页面使用根目录的 `skills.sh.json` 分组，新 Skill 应同时加入合适的分组。

预计访问地址：

- 仓库：<https://skills.sh/BITFSAE/bitfsae-skills>
- Skill：<https://skills.sh/BITFSAE/bitfsae-skills/bitfsae-project-standards>
- Skill：<https://skills.sh/BITFSAE/bitfsae-skills/bitfsae-github-workflow>

### OpenAI Skills API

OpenAI Skills API 以单个 Skill 目录或 ZIP 为上传单位。先验证并生成可复现的 ZIP：

```bash
python3 tools/validate_skills.py
python3 tools/package_skills.py
```

产物位于 `dist/<skill-name>.zip`，不提交 Git。创建 OpenAI Skill：

```bash
curl https://api.openai.com/v1/skills \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "files=@dist/bitfsae-project-standards.zip"
```

记录响应中的 `skill_...` ID。后续更新创建不可变版本，并把它设为默认版本：

```bash
curl https://api.openai.com/v1/skills/skill_.../versions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "files=@dist/bitfsae-project-standards.zip" \
  -F "default=true"
```

Skill ID 属于具体 OpenAI 项目，不写入仓库；API Key 只通过环境变量提供。每个 Skill 独立创建和更新，不把整个多 Skill 仓库打成一个 OpenAI Skill。

## 参与维护

1. 从最新 `main` 创建分支；
2. 一个 PR 聚焦一个 Skill 或一项仓库基础设施修改；
3. 修改 Skill 时同步检查触发描述、正文、references、`agents/openai.yaml` 和 `translations/zh-CN/` 对应镜像；
4. 执行 `python3 tools/validate_skills.py`；
5. 更新 `CHANGELOG.md`，通过 CI 和维护者审核后按维护者选择的方式合并。

详细要求见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 公开仓库边界

不得加入密码、Token、私钥、生产服务器地址、个人信息、未脱敏日志或无权公开的车队/厂家资料。Skill 可以描述凭据应如何管理，但不能包含真实值。

## 许可证

本仓库采用 [MIT License](LICENSE)。不要加入来源和授权不清楚的第三方 Skill、脚本或模板。

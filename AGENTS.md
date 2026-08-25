# AI 代码与文档规范

## Skill 修改

- 修改或新增 Skill 时遵循 Skill Creator 规范，并保持一个 Skill 一个独立目录。
- Frontmatter 的 `description` 必须明确触发和不触发场景，不得为了提高调用率写成宽泛描述。
- 核心流程放在 `SKILL.md`；详细规则按需放入一级 `references/`，避免重复。
- 修改能力或触发范围后，同步检查 `agents/openai.yaml` 和 `translations/zh-CN/` 对应镜像。
- 不加入真实密码、Token、私钥、生产地址、个人信息或无权公开的资料。

## 文档与验证

- 根目录 README 负责仓库入口和 Skill 索引；各 Skill 不创建自己的 README、安装指南或更新日志。
- 已完成修改和待办统一维护在根目录 `CHANGELOG.md`。
- 修改后运行 `python3 tools/validate_skills.py`，并检查 Git 差异中没有缓存、构建产物和敏感信息。
- 使用清楚、直接的中文，避免说教、冗余和在多个文件中重复相同规则。

DO NOT send optional commentary

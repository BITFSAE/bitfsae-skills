# 参与维护

## 新增 Skill

- 目录名使用小写字母、数字和连字符，并与 `SKILL.md` 的 `name` 完全一致；
- 使用 Skill Creator 初始化和验证，不手写不完整的目录骨架；
- Frontmatter 只保留 `name` 和 `description`；
- `description` 同时说明能力、应触发的场景和不应触发的场景，避免使用"所有项目""任何代码任务"等过宽表述；
- `SKILL.md` 只放核心流程，较长的领域规则放在一级 `references/`；
- 不创建 Skill 自己的 README、安装指南或更新日志；仓库级 README 和 CHANGELOG 统一承担这些职责；
- `agents/openai.yaml` 的默认提示必须明确引用 `$skill-name`。

## 修改现有 Skill

先说明真实使用中出现的问题，例如误触发、步骤缺失、规则过严或项目适配不足。只修改解决该问题所需的内容，不借机加入与 Skill 目标无关的规范。

如果修改了能力范围或触发范围，应同步核对：

- Frontmatter `description`；
- `agents/openai.yaml` 的名称、简介和默认提示；
- 引用文件的路由是否仍准确；
- 原有使用场景是否被意外破坏。

## Pull Request

- 普通修改至少需要 1 名 `skill-maintainers` 审核；
- 大幅改变触发条件、权限边界或外部工具操作的修改，需要说明兼容性和误触发风险；
- 不直接推送 `main`，不强制推送，不改写已发布 Tag；
- PR 中写明验证命令和结果；
- 新增或修改内容同步写入根目录 `CHANGELOG.md`。

## 验证

```bash
python3 -m pip install --requirement requirements-dev.txt
python3 tools/validate_skills.py
```

自动检查只验证结构和明显错误，不能替代对触发范围、操作安全和实际项目适配性的审核。

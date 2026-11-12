# 更新记录

## 未发布

### 已完成

- 更新 `bitfsae-project-standards` 的写作规范（`references/writing-style.md` 及关联引用与中文镜像）：补充按文档用途（仓库契约、设计计算与审车材料、内部学习积累与评审）区分语气的要求，明确区分禁用情绪词与带定量依据的工程判断，增加量级反证与扫读可读性要求。
- 更新 `can-dbc-edit`：实测团队 DBC 发现，用 `sort_signals=None` 加载的数据库无法解码 Intel 信号按起始位从高到低排列的报文，解码校验改按默认顺序加载，并新增 `validate_dbc.py --decode-check`；cantools 导出会丢掉 Vector 虚拟报文 `VECTOR__INDEPENDENT_SIG_MSG`（连同信号和注释）而语义 diff 看不出，`--compare` 与 `edit_dbc.py` 改为报告原始语句计数并在丢失时告警。补充 CANdb++ 长名称（`SystemSignalLongSymbol`）、`GenMsgCycleTime` 默认值和 `GenSigStartValue` 原始值的说明；脚本的编码尝试顺序与文档一致（含 `utf-8-sig`、`gbk`），未安装 `cancompare` 时跳过而不是报错退出。新增 `scripts/testdata/layout_quirks.dbc`，同步中文镜像。
- 为 `bitfsae-project-standards` 新增 `references/writing-style.md` 及中文镜像，集中文档写作要求：平实工程化语句，禁用商业化用词、夸张、自评式论断和绝对化词汇，正面表述与否定句，用语平实，文档顺序，完整性优先于简短，修订自查清单。同步在 `SKILL.md` 和 `documentation-system.md` 中引用，并补充接口文档只写可观测内容、已实现行为与后续工作分开的要求。
- 新增 `can-dbc-edit`（来自队内 Codex skill v1.1，MIT 授权）：基于 cantools/canmatrix 的 DBC 编辑、校验与 CANdb++ 兼容修复。入库时去掉 frontmatter 中的 license/metadata 字段以通过仓库校验，正文与脚本保持原版，并补齐 `agents/openai.yaml` 和 `translations/zh-CN/` 中文镜像；同时在 README 和 `skills.sh.json` 增加“CAN/DBC 工具”分组登记。
- 新增 `bitfsae-github-workflow`，覆盖分支、提交、PR 审查、共享接口同步和安全边界，并保持触发范围与约束精简。
- 新增 `translations/zh-CN/` 中文镜像，不参与安装、打包与发布，仅用于队内阅读和与英文原版同步。
- 建立 BITFSAE 多 Skill 公共仓库结构、贡献规范和自动校验。
- 迁入 `bitfsae-project-standards` 作为首个共享 Skill。
- 为项目规范 Skill 增加按需同步 `BITFSAE/vehicle-interfaces` 的判断和流程。
- 保持项目规范 Skill 的窄触发范围，避免普通代码、构建、Git 和单篇文档任务误触发。
- 增加 skills.sh 多 Skill 仓库页面配置、CLI 安装说明和配置校验。
- 增加 OpenAI Skills API 的独立打包工具与创建、版本更新流程。
- 确定仓库采用 MIT License 公开发布。
- 单一维护者阶段取消强制人工批准，并移除尚不存在的 Code Owner 团队引用。

### 待办

- 下一名维护者加入后完成一次新增或修改 Skill 的 PR 演练。

---
name: can-dbc-edit
description: 编辑、修补、校验或重写 CAN DBC（.dbc）文件，不手写 BO_/SG_ 语法。当用户修改报文、信号、缩放/偏移、单位、注释、值表、周期、多路复用、字节序，或要求修复无法解析的 DBC、CANdb++ 语法错误、节顺序、GBK 编码问题时触发。优先用 cantools/canmatrix 对象编辑加严格解析。也用于 cancompare 和 Motorola/Intel 布局调整。
---

# CAN DBC 编辑

编辑 DBC 文件，保证结果始终可以解析。绝不从模型直接输出整个 DBC。

## 硬性规则

- 不要从零手写 `BO_`、`SG_`、`VAL_`、`BA_`、`CM_` 行。
- 不要在 `BO_` 里编造十六进制 ID（ID 是十进制；扩展 ID 用 Vector 高位编码）。
- 不要心算 Motorola 起始位或位打包。用库。
- 不要交付一个过不了 `scripts/validate_dbc.py --strict` 的文件。
- 未被要求改动的内容全部保留——ID、起始位、长度、字节序、有无符号、多路复用 `M`/`mN`、节点、发送方/接收方、属性、注释、值表、信号组、编码、CRLF、信号顺序。

## 选择路径

**路径 A——外科手术式（默认）。** 在已有行上做孤立字段修改——缩放系数、偏移、最小/最大值、单位、注释、VAL_ 标签、周期属性。

1. `python3 scripts/validate_dbc.py --strict <file.dbc>`
2. 定位到确切行（`grep` / 读文件）。只改那些字符。
3. 再校验一次。解析失败就回退。不要通过重写文件来"修复"一个坏的导出。

**路径 B——结构化重写。** 增删或重排报文/信号、改布局、字节序、多路复用，或新建数据库。

1. 把原始文件复制为 `<file>.dbc.bak`。
2. 把操作写进一个 JSON 文件（见 `references/ops-schema.md`）。
3. `python3 scripts/edit_dbc.py <in.dbc> <out.dbc> <ops.json>`
4. `python3 scripts/validate_dbc.py --strict --cross-check <out.dbc>`
5. `python3 scripts/validate_dbc.py --compare <in.dbc> <out.dbc>`
6. 展示 compare 摘要和文本 diff。完成的标准是干净语义 diff 加严格解析通过——不是 git diff 很小。

如果路径 B 会丢掉必须保留的属性、注释、多路复用或信号组，停下来改用路径 A 或拆分任务。

**路径 C——CANdb++ / Vector 编辑器打不开文件。** 文件可能在 cantools 里本来就能解析。不要通过 cantools 导出来"修复"它。

1. 把原始文件复制为 `<file>.dbc.bak`。
2. `python3 scripts/normalize_candbpp.py IN.dbc artifacts/<stem>_candbpp`
   生成 UTF-8、GBK 和 UTF-8-BOM 三个变体（CRLF、注释展开为单行、`VAL_` 移到所有 `BO_` 之后）。
3. 用 `--strict --cross-check` 校验 UTF-8 副本，并与原文件 `--compare`。
4. 中文 Windows CANdb++ 优先给用户 **GBK** 文件。UTF-8 BOM 作为备选。
5. 让用户 File → Open 打开新路径。CANdb++ 报的行号通常是过早出现的 `CM_`/`VAL_` 之后的第一个 `BO_`，不是真正的缺陷位置。

细节见 [references/candbpp.md](references/candbpp.md)。

## 必需命令

Skill 根目录下的脚本（在 skill 目录里运行，或传绝对路径）：

```bash
python3 scripts/validate_dbc.py --strict FILE.dbc
python3 scripts/validate_dbc.py --strict --cross-check FILE.dbc
python3 scripts/validate_dbc.py --compare OLD.dbc NEW.dbc
python3 scripts/edit_dbc.py IN.dbc OUT.dbc OPS.json
python3 scripts/normalize_candbpp.py IN.dbc OUT_STEM
```

依赖——`pip install cantools canmatrix`。缺失时先安装再编辑。

脚本使用的加载规则：

- 每次写入后 `strict=True`
- 加载和导出都用 `sort_signals=None`（不让 cantools 重排位）
- 依次尝试编码 `utf-8`、`utf-8-sig`、`gbk`、`cp1252`、`latin-1`
- DBC 输出用 `\r\n`
- cantools `strict` 加载拒绝 UTF-8 BOM——校验无 BOM 副本
- 中文 Windows CANdb++ 通常要 GBK，不是 UTF-8

## 声明完成前

报告全部内容：

- 使用的路径（A、B 或 C）
- 报文 / 信号 / 字段 / 旧值 → 新值
- 校验命令输出
- 文本 diff（仓库里用 `git diff -- FILE.dbc`，否则 `diff -u`）
- 路径 B 或关键改动时的 `cancompare` / `--compare` 摘要

cantools 和 canmatrix 结论不一致时，两边都报告，不交付。

## 禁止事项

- 仅仅为了"规范化"用户没要求重排格式的文件而导出再重载。
- 在同一步里混合路径 A 行编辑和路径 B 导出。
- 心算 `@0`/`@1` 起始位。
- 目标工具是 CANdb++ 时，把 `CM_` / `VAL_` 留在 `BO_` 块之间交错。
- 文件里有中文注释时，只给用户一个 UTF-8 无 BOM 文件作为唯一 CANdb++ 交付物。

细节见 [references/ops-schema.md](references/ops-schema.md)、[references/pitfalls.md](references/pitfalls.md)、[references/candbpp.md](references/candbpp.md)。

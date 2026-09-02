# 模型容易写错的 DBC 陷阱

## 必须由库生成的语法

- `BO_` 帧 ID 是十进制，绝不能写 `0x123`。
- 29 位 / 扩展 ID 在 Vector DBC 文件里存的是 `id | 0x80000000`。cantools 暴露 `frame_id` 加 `is_extended_frame`。调 API 时不要自己加高位。
- `SG_` 形状——`Name : start|length@endian sign (factor,offset) [min|max] "unit" Recv`
  - `@0` = Motorola / 大端
  - `@1` = Intel / 小端
  - `+` 无符号，`-` 有符号
- 每条 `BO_`、`SG_`、`VAL_`、`CM_`、`BA_` 语句以 `;` 结尾（信号行沿用导出器使用的报文终止符风格）。
- 官方导出使用 Windows CRLF（`\r\n`）。

## Motorola 起始位

`@0` 的 Vector 起始位不是"线性位索引下信号的最低位"。不要在头脑里换算字节/位图。从 cantools 读 `signal.start` 和 `signal.byte_order`，或只在用户给出值的情况下用 `set_layout` 改布局。

## 导出允许破坏什么

`load_file` + `dump_file` 不是无损的。常见丢失：

- 自定义 `BA_DEF_` / 部分属性
- `SIG_GROUP_`
- 环境变量
- `VAL_TABLE_` 与信号内 `VAL_` 的区别
- 注释编码（OEM 文件常用 CP1252）
- 未使用的节点
- 原始信号排列顺序（`sort_signals=None` 只能缓解，不能消除）

用户需要保留这些时，留在路径 A。

## cantools 加载参数

```python
cantools.database.load_file(
    path,
    strict=True,
    sort_signals=None,
)
```

`strict=True` 拒绝重叠信号。只用 `strict=False` 诊断已经加载失败的文件。

路径 B 必须用时，为减少导出扰动：

```python
cantools.database.dump_file(db, out, sort_signals=None)
```

## 双解析器分歧

cantools 和 canmatrix 对某些多路复用、J1939 和不规范文件结论不一致。

- 原文件在两边都能加载，编辑后的文件在一边失败——回退。
- 原文件本来就过不了某个解析器——作为既有问题报告。除非用户要求，不要"修复"。

## 编码

依次尝试 `utf-8`、`utf-8-sig`、`gbk`、`cp1252`、`latin-1`。
给库用的导出保持 UTF-8 无 BOM。

中文注释加 UTF-8 无 BOM，是 CANdb++ 在注释之后几十行才报语法错误的常见原因。中文 Windows 优先给 GBK（CP936）加 CRLF。见 [candbpp.md](candbpp.md)。

## CANdb++ 节顺序

cantools 容忍 `CM_` 跟在每个 `BO_` 下面。CANdb++ 不容忍。
一旦见过 `CM_` 或 `VAL_`，再出现 `BO_` 就是语法错误。它打印的行号（通常是下一条真实报文，例如 382 或 618 行）只是症状。

用 `scripts/normalize_candbpp.py` 规范化。不要用 cantools 导出。

还要把多行引号注释拍平成单行、把 `VAL_` 放在 `SIG_VALTYPE_` 之前、这两类以 ` ;` 结尾，并在用到时把 `Vector__XXX` 加进 `BU_:`。

## 扩展 ID 十进制不是溢出

`BO_ 2550588916` 就是 `0x1806E5F4 | 0x80000000`。保留它。不要改写成只含 29 位 ID，也不要把 `> 2147483647` 当作非法。

## 校验不等于解码

文件能解析不代表起始位正确。改布局后，如果用户给了已知原始帧，解码验证：

```python
db.get_message_by_name("EngineData").decode(bytes.fromhex("0102030405060708"))
```

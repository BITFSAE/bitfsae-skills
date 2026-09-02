# Vector CANdb++ 兼容性（实战记录）

这些规则来自修复 `Vehicle_CanA/B/C/1.dbc`：这些文件在 cantools 里能解析，
在 CANdb++ 里却报某一行语法错误。

## 行号通常意味着什么

CANdb++ 使用单遍语法。报出的行往往**不是**坏 token 本身，而是*当前节里*
非法的第一个 token。

典型对应关系：

- 在靠后的 `BO_` 上报错（CanB 原版约 382 / 618 行，Can1 在每条注释后）
  ——已经出现过 `CM_` 或 `VAL_`，之后又出现了新报文。
- 在 `SIG_VALTYPE_` / `VAL_` 附近报错
  ——节顺序问题，或 `SIG_VALTYPE_` 排在 `VAL_` 之前。
- 在中文注释之后几行报错
  ——编码不匹配。UTF-8 字节被当作 GBK/CP1252 读入，引号断裂，
  解析器在靠后的行才恢复。

不要先去"修"报出的那一行。检查节顺序和编码。

## CANdb++ 要求的顶层顺序

保持这个顺序。空行无所谓。交错不行。

1. `VERSION`
2. `NS_`（存在时保留完整 Vector 符号列表）
3. `BS_:`
4. `BU_:`
5. 所有 `BO_` 及其 `SG_` 行（报文之间不插注释）
6. 全部 `CM_`
7. `BA_DEF_` / `BA_DEF_DEF_`
8. `BA_`
9. 全部 `VAL_`
10. `SIG_VALTYPE_` 最后

`CM_`/`VAL_` 之后再出现 `BO_` 是 CANdb++ 最常见的硬失败。

## 中文 Windows CANdb++ 的编码

同一批文件上试过：

| 编码 | 结果 |
|---|---|
| UTF-8 无 BOM、LF | 经常语法错误；行号漂移 |
| UTF-8 BOM、CRLF | 较新的 CANdb++ 可能打开 |
| **GBK（CP936）、CRLF** | 在用户的 CANdb++ 上打开成功 |

用户在中文 Windows CANdb++ 上时，优先交付 **GBK + CRLF**。
同时保留一份 UTF-8 无 BOM 副本给 cantools（`strict=True` 拒绝 BOM）。
GBK 仍失败时，UTF-8 BOM 是备选。

`°` 和中文注释在 GBK 里可编码。遇到无法编码的字符，停下来问——
不要静默替换。

## CANdb++ 在意的语句细节

- `VAL_` 和 `SIG_VALTYPE_` 应以 ` ;` 结尾（分号前有空格）。
- 注释必须是单个物理行。`"..."` 内的换行对某些写出器合法，
  对 CANdb++ 致命。拍平成单个空格。
- `BO_` / `SG_` **不**以 `;` 结尾。不要凭空加。
- 任何信号或占位节点用到 `Vector__XXX` 时，把它加进 `BU_:`。
- 扩展 ID 保持十进制且第 31 位置位（`id | 0x80000000`）。超过
  `2^31-1` 的值是正确的，不是溢出。例：`0x1806E5F4` → `2550588916`。
- `VECTOR__INDEPENDENT_SIG_MSG`（`3221225472`）是 Vector 占位帧。
  保留它。其内部重复的未使用信号名是既有情况；除非用户要求，不要重命名。

## 不走路径 B 导出的规范化方法

不要为了取悦 CANdb++ 而 `load_file` + `dump_file`。那种重写会丢属性，
还可能改变 Motorola 起始位。

用 `scripts/normalize_candbpp.py`（块重排 + 编码 + CRLF）。
然后：

```bash
python3 scripts/validate_dbc.py --strict --cross-check OUT_utf8.dbc
python3 scripts/validate_dbc.py --compare IN.dbc OUT_utf8.dbc
```

compare 应为 0 个信号/布局差异。拍平多行 `CM_` 后注释空白被折叠是
可接受的。把 `Vector__XXX` 加进 `BU_` 是可接受的。

## CANdb++ 修复任务的交付物

每个源文件写三份：

- `<stem>_candbpp_gbk.dbc`——优先给 CANdb++
- `<stem>_candbpp_utf8bom.dbc`——备选
- `<stem>_candbpp.dbc`——UTF-8 无 BOM，给 cantools / git

让用户 **File → Open** 打开新路径。刷新旧缓冲区看到的还是旧行号。

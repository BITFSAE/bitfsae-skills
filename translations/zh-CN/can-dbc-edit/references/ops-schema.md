# edit_dbc.py 操作

传入一个 JSON 对象：

```json
{
  "ops": [
    {
      "op": "set_signal",
      "message": "EngineData",
      "signal": "VehicleSpeed",
      "fields": {
        "scale": 0.01,
        "offset": 0,
        "minimum": 0,
        "maximum": 250,
        "unit": "km/h",
        "comment": "Wheel-based vehicle speed"
      }
    }
  ]
}
```

未知字段名是错误。只写列出的字段。

## 操作列表

### `set_signal`

设置已有信号的标量字段。

允许的 `fields` 键——`scale`、`offset`、`minimum`、`maximum`、`unit`、`comment`、`is_signed`、`is_float`。

除非用户明确要求改布局，不要在这里放 `start`、`length`、`byte_order` 或 `name`。那些用 `set_layout` 或 `rename_signal`。

### `set_choices`

替换值表。

```json
{
  "op": "set_choices",
  "message": "EngineData",
  "signal": "EngineState",
  "choices": {"0": "Off", "1": "Cranking", "2": "Running"}
}
```

键可以是字符串或整数。空对象清除值表。

### `set_cycle_time`

```json
{"op": "set_cycle_time", "message": "EngineData", "cycle_time": 10}
```

`cycle_time` 单位是毫秒。用 `null` 清除。

### `set_comment`

`scope` 取 `database`、`message` 或 `signal`。

```json
{"op": "set_comment", "scope": "message", "message": "EngineData", "comment": "10ms cyclic"}
```

signal 作用域还需要 `"signal": "Name"`。

### `rename_signal`

```json
{"op": "rename_signal", "message": "EngineData", "signal": "Spd", "new_name": "VehicleSpeed"}
```

### `rename_message`

```json
{"op": "rename_message", "message": "EngineData", "new_name": "VCU_EngineData"}
```

不改变帧 ID。

### `set_frame_id`

只在用户要求改 ID 时使用。

```json
{"op": "set_frame_id", "message": "EngineData", "frame_id": 291, "is_extended_frame": false}
```

`frame_id` 是整数（十进制）。绝不传十六进制字符串。

### `set_layout`

只在用户要求移位或改字节序时使用。

```json
{
  "op": "set_layout",
  "message": "EngineData",
  "signal": "VehicleSpeed",
  "start": 0,
  "length": 16,
  "byte_order": "little_endian"
}
```

`byte_order` 取 `little_endian`（Intel，`@1`）或 `big_endian`（Motorola，`@0`）。不要自己算 `start`——从用户那里拿，或从当前信号的库导出里拿。

### `add_signal`

追加一个信号。需要完整定义。此操作后脚本会刷新报文。

```json
{
  "op": "add_signal",
  "message": "EngineData",
  "name": "OilTemp",
  "start": 16,
  "length": 8,
  "byte_order": "little_endian",
  "is_signed": false,
  "scale": 1,
  "offset": -40,
  "minimum": -40,
  "maximum": 215,
  "unit": "degC",
  "receivers": ["VCU"]
}
```

### `delete_signal`

```json
{"op": "delete_signal", "message": "EngineData", "signal": "OilTemp"}
```

### `add_message`

```json
{
  "op": "add_message",
  "name": "BMS_Status",
  "frame_id": 400,
  "length": 8,
  "senders": ["BMS"],
  "is_extended_frame": false,
  "cycle_time": 100,
  "comment": "BMS status"
}
```

信号用后续的 `add_signal` 操作添加。

### `delete_message`

```json
{"op": "delete_message", "message": "BMS_Status"}
```

## 说明

- 名称区分大小写，必须与文件一致。
- 路径 B 即使只改一个字段也会重排 DBC 文本。单行修改优先路径 A。
- 强制 `sort_signals=None`，文件里的位序不会被悄悄重排。

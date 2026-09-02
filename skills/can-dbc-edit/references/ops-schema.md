# edit_dbc.py operations

Pass a JSON object:

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

Unknown field names are an error. Only listed fields are written.

## Ops

### `set_signal`

Set scalar fields on an existing signal.

Allowed `fields` keys — `scale`, `offset`, `minimum`, `maximum`, `unit`, `comment`, `is_signed`, `is_float`.

Do not put `start`, `length`, `byte_order`, or `name` here unless the user explicitly requested a layout change. For those use `set_layout` or `rename_signal`.

### `set_choices`

Replace the value table.

```json
{
  "op": "set_choices",
  "message": "EngineData",
  "signal": "EngineState",
  "choices": {"0": "Off", "1": "Cranking", "2": "Running"}
}
```

Keys may be strings or ints. Empty object clears choices.

### `set_cycle_time`

```json
{"op": "set_cycle_time", "message": "EngineData", "cycle_time": 10}
```

`cycle_time` is milliseconds. Use `null` to clear.

### `set_comment`

`scope` is `database`, `message`, or `signal`.

```json
{"op": "set_comment", "scope": "message", "message": "EngineData", "comment": "10ms cyclic"}
```

Signal scope also needs `"signal": "Name"`.

### `rename_signal`

```json
{"op": "rename_signal", "message": "EngineData", "signal": "Spd", "new_name": "VehicleSpeed"}
```

### `rename_message`

```json
{"op": "rename_message", "message": "EngineData", "new_name": "VCU_EngineData"}
```

Does not change the frame ID.

### `set_frame_id`

Only when the user asked to change the ID.

```json
{"op": "set_frame_id", "message": "EngineData", "frame_id": 291, "is_extended_frame": false}
```

`frame_id` is integer (decimal). Never pass a hex string.

### `set_layout`

Only when the user asked to move bits or change endianness.

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

`byte_order` is `little_endian` (Intel, `@1`) or `big_endian` (Motorola, `@0`). Do not compute `start` yourself — take it from the user or from a library dump of the current signal.

### `add_signal`

Appends a signal. Requires a complete definition. After this op the script refreshes the message.

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

Signals are added in later `add_signal` ops.

### `delete_message`

```json
{"op": "delete_message", "message": "BMS_Status"}
```

## Notes

- Names are case-sensitive and must match the file.
- Path B will reformat DBC text even for a one-field change. Prefer Path A for one-liners.
- `sort_signals=None` is forced so bit order in the file is not silently resorted.

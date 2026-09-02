# DBC pitfalls the model gets wrong

## Syntax the library must emit

- `BO_` frame ID is decimal, never `0x123`.
- 29-bit / extended IDs in Vector DBC store `id | 0x80000000` in the file. cantools exposes `frame_id` plus `is_extended_frame`. Do not add the high bit yourself when calling the API.
- `SG_` shape — `Name : start|length@endian sign (factor,offset) [min|max] "unit" Recv`
  - `@0` = Motorola / big endian
  - `@1` = Intel / little endian
  - `+` unsigned, `-` signed
- Every `BO_`, `SG_`, `VAL_`, `CM_`, `BA_` statement ends with `;` (signal lines inherit the message terminator style used by the exporter).
- Official dumps use Windows CRLF (`\r\n`).

## Motorola start bit

Vector start bit for `@0` is not "LSB of the signal in a linear bit index". Do not convert byte/bit diagrams in your head. Read `signal.start` and `signal.byte_order` from cantools, or change layout only with `set_layout` using values the user supplied.

## What dump is allowed to destroy

`load_file` + `dump_file` is not lossless. Common losses:

- custom `BA_DEF_` / some attributes
- `SIG_GROUP_`
- environment variables
- `VAL_TABLE_` vs in-signal `VAL_`
- comment encoding (OEM files are often CP1252)
- unused nodes
- original signal listing order (mitigated by `sort_signals=None`, not eliminated)

If the user needs those preserved, stay on Path A.

## cantools load knobs

```python
cantools.database.load_file(
    path,
    strict=True,
    sort_signals=None,
)
```

`strict=True` rejects overlapping signals. Use `strict=False` only to diagnose a file that already will not load.

To minimize dump churn when Path B is required:

```python
cantools.database.dump_file(db, out, sort_signals=None)
```

## Dual parser disagreement

cantools and canmatrix disagree on some multiplex, J1939, and sloppy files.

- If the original file loads in both and the edited file fails in one — revert.
- If the original already fails one parser, report that as pre-existing. Do not "fix" it unless asked.

## Encoding

Try `utf-8`, then `utf-8-sig`, then `gbk`, then `cp1252`, then `latin-1`.
When dumping for libraries, keep UTF-8 without BOM.

Chinese comments plus UTF-8 without BOM is the usual reason CANdb++ reports
a syntax error tens of lines after the comment. On Chinese Windows give GBK
(CP936) with CRLF first. See [candbpp.md](candbpp.md).

## CANdb++ section order

cantools is tolerant of `CM_` sitting under each `BO_`. CANdb++ is not.
Once it has seen `CM_` or `VAL_`, a later `BO_` is a syntax error. The
line it prints (often the next real message, e.g. line 382 or 618) is a
symptom.

Normalize with `scripts/normalize_candbpp.py`. Do not cantools-dump.

Also flatten multiline quoted comments, put `VAL_` before `SIG_VALTYPE_`,
end those two with ` ;`, and add `Vector__XXX` to `BU_:` when it is used.

## Extended ID decimals are not overflow

`BO_ 2550588916` is `0x1806E5F4 | 0x80000000`. Keep it. Do not rewrite as
the 29-bit ID only, and do not treat `> 2147483647` as invalid.

## Validation is not decoding

A file can parse and still have the wrong start bit. After layout changes, decode a known raw frame if the user provided one:

```python
db.get_message_by_name("EngineData").decode(bytes.fromhex("0102030405060708"))
```

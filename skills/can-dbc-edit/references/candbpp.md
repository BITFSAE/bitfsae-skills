# Vector CANdb++ compatibility (field notes)

These rules come from repairing `Vehicle_CanA/B/C/1.dbc` that parsed in cantools
but failed in CANdb++ with a line-number syntax error.

## What the line number usually means

CANdb++ uses a one-pass grammar. The reported line is often **not** the broken
token. It is the first token that is illegal *in the current section*.

Typical mappings:

- Error on a later `BO_` (CanB original ~382 / ~618, Can1 after each comment)
  — a `CM_` or `VAL_` already started, then another message appeared.
- Error near `SIG_VALTYPE_` / `VAL_`
  — section order, or `SIG_VALTYPE_` placed before `VAL_`.
- Error a few lines after Chinese comments
  — encoding mismatch. UTF-8 bytes were read as GBK/CP1252, quotes broke,
  and the parser recovered at a later line.

Do not "fix" the reported line first. Inspect section order and encoding.

## Required top-level order for CANdb++

Keep this order. Blank lines are fine. Interleaving is not.

1. `VERSION`
2. `NS_` (full Vector symbol list if present)
3. `BS_:`
4. `BU_:`
5. Every `BO_` + its `SG_` lines (no comments between messages)
6. All `CM_`
7. `BA_DEF_` / `BA_DEF_DEF_`
8. `BA_`
9. All `VAL_`
10. `SIG_VALTYPE_` last

`BO_` after `CM_`/`VAL_` is the most common CANdb++ hard fail.

## Encoding for Chinese Windows CANdb++

Tried on the same files:

| Encoding | Result |
|---|---|
| UTF-8, no BOM, LF | often syntax error; line number drifts |
| UTF-8 BOM, CRLF | newer CANdb++ may open |
| **GBK (CP936), CRLF** | opened on the user's CANdb++ |

Ship **GBK + CRLF** first when the user is on Chinese Windows CANdb++.
Also keep a UTF-8 no-BOM copy for cantools (`strict=True` rejects a BOM).
UTF-8 BOM is the fallback if GBK still fails.

`°` and Chinese comments encode in GBK. If a character cannot encode, stop
and ask — do not silently replace.

## Statement hygiene CANdb++ cares about

- `VAL_` and `SIG_VALTYPE_` should end with ` ;` (space before semicolon).
- Comments must be one physical line. Newlines inside `"..."` are legal in
  some writers and fatal in CANdb++. Flatten to a single space.
- `BO_` / `SG_` do **not** end with `;`. Do not invent one.
- If any signal or dummy node uses `Vector__XXX`, add it to `BU_:`.
- Extended IDs stay decimal with bit 31 set (`id | 0x80000000`). Values
  above `2^31-1` are correct, not overflow. Example:
  `0x1806E5F4` → `2550588916`.
- `VECTOR__INDEPENDENT_SIG_MSG` (`3221225472`) is a Vector dummy frame.
  Keep it. Duplicate unused signal names inside it are pre-existing; do
  not rename unless asked.

## How to normalize without a Path B dump

Do **not** `load_file` + `dump_file` just to please CANdb++. That rewrite
drops attributes and can change Motorola start bits.

Use `scripts/normalize_candbpp.py` (block reorder + encoding + CRLF).
Then:

```bash
python3 scripts/validate_dbc.py --strict --cross-check OUT_utf8.dbc
python3 scripts/validate_dbc.py --compare IN.dbc OUT_utf8.dbc
```

Compare should be 0 signal/layout diffs. Comment whitespace collapse after
flattening multiline `CM_` is acceptable. Adding `Vector__XXX` to `BU_` is
acceptable.

## Deliverables for a CANdb++ repair

Write three files per source:

- `<stem>_candbpp_gbk.dbc` — give this to CANdb++ first
- `<stem>_candbpp_utf8bom.dbc` — fallback
- `<stem>_candbpp.dbc` — UTF-8 no BOM, for cantools / git

Tell the user to **File → Open** the new path. Refreshing the old buffer
keeps the old line numbers.

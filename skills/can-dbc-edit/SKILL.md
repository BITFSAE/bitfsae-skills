---
name: can-dbc-edit
description: Edit, patch, validate, or rewrite CAN DBC (.dbc) files without hand-writing BO_/SG_ syntax. Use when the user changes messages, signals, scale/offset, units, comments, value tables, cycle time, multiplex, byte order, or asks to fix invalid DBC / CANdb++ syntax errors / section order / GBK encoding. Prefer cantools/canmatrix object edits plus strict parse. Also use for cancompare and Motorola/Intel layout changes.
---

# CAN DBC Edit

Edit DBC files so the result always parses. Never emit a full DBC from the model.

## Hard rules

- Do not write `BO_`, `SG_`, `VAL_`, `BA_`, or `CM_` lines from scratch.
- Do not invent hex IDs in `BO_` (IDs are decimal; extended IDs use the Vector high-bit encoding).
- Do not hand-compute Motorola start bits or bit packing. Use the library.
- Do not ship a file that fails `scripts/validate_dbc.py --strict`.
- Preserve everything not requested — IDs, start bit, length, byte order, signedness, multiplex `M`/`mN`, nodes, senders/receivers, attributes, comments, value tables, signal groups, encoding, CRLF, signal order.

## Choose a path

**Path A — surgical (default).** Isolated field change on an existing line — factor, offset, min/max, unit, comment, VAL_ label, cycle-time attribute.

1. `python3 scripts/validate_dbc.py --strict <file.dbc>`
2. Locate the exact line (`grep` / read). Change only those characters.
3. Validate again. If parse fails, revert. Do not "fix" a broken dump by rewriting the file.

**Path B — structured rewrite.** Add/delete/reorder messages or signals, change layout, endianness, multiplex, or create a new database.

1. Copy the original to `<file>.dbc.bak`.
2. Put operations in a JSON file (see `references/ops-schema.md`).
3. `python3 scripts/edit_dbc.py <in.dbc> <out.dbc> <ops.json>`
4. `python3 scripts/validate_dbc.py --strict --cross-check <out.dbc>`
5. `python3 scripts/validate_dbc.py --compare <in.dbc> <out.dbc>`
6. Show the compare summary and a text diff. Completion is a clean semantic diff plus a passing strict parse — not a tiny git diff.

If Path B would drop attributes, comments, multiplex, or signal groups that must stay, stop and use Path A or split the work.

**Path C — CANdb++ / Vector editor will not open the file.** The file may already parse in cantools. Do not dump through cantools to "fix" it.

1. Copy the original to `<file>.dbc.bak`.
2. `python3 scripts/normalize_candbpp.py IN.dbc artifacts/<stem>_candbpp`
   writes UTF-8, GBK, and UTF-8-BOM variants (CRLF, comments unwrapped, `VAL_` after all `BO_`).
3. Validate the UTF-8 copy with `--strict --cross-check` and `--compare` against the original.
4. Give the user the **GBK** file first on Chinese Windows CANdb++. UTF-8 BOM is fallback.
5. Tell them to File → Open the new path. The CANdb++ line number is usually the first `BO_` after a premature `CM_`/`VAL_`, not the real defect.

Details — [references/candbpp.md](references/candbpp.md).

## Required commands

Skill-root scripts (run from the skill directory, or pass absolute paths):

```bash
python3 scripts/validate_dbc.py --strict FILE.dbc
python3 scripts/validate_dbc.py --strict --cross-check FILE.dbc
python3 scripts/validate_dbc.py --compare OLD.dbc NEW.dbc
python3 scripts/edit_dbc.py IN.dbc OUT.dbc OPS.json
python3 scripts/normalize_candbpp.py IN.dbc OUT_STEM
```

Dependencies — `pip install cantools canmatrix`. If missing, install before editing.

Load rules used by the scripts:

- `strict=True` after every write
- `sort_signals=None` on load and dump (do not let cantools reorder bits)
- try encodings `utf-8`, `utf-8-sig`, `gbk`, `cp1252`, `latin-1`
- DBC output uses `\r\n`
- cantools `strict` load rejects a UTF-8 BOM — validate the no-BOM copy
- Chinese Windows CANdb++ usually wants GBK, not UTF-8

## Before claiming done

Report all of:

- path used (A, B, or C)
- message / signal / field / old → new
- validation command output
- text diff (`git diff -- FILE.dbc` if in a repo, else `diff -u`)
- `cancompare` / `--compare` summary when Path B or the change is critical

If cantools and canmatrix disagree, report both and do not ship.

## Do not

- Dump and reload just to "normalize" a file the user did not ask to reformat.
- Mix Path A line edits with a Path B dump in the same step.
- Calculate `@0`/`@1` start bits in your head.
- Leave `CM_` / `VAL_` interleaved between `BO_` blocks when the target tool is CANdb++.
- Hand the user a UTF-8 no-BOM file as the only CANdb++ deliverable if the file has Chinese comments.

Details — [references/ops-schema.md](references/ops-schema.md), [references/pitfalls.md](references/pitfalls.md), [references/candbpp.md](references/candbpp.md).

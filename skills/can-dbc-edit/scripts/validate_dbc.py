#!/usr/bin/env python3
"""Validate a DBC with cantools (required) and optionally canmatrix."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ENCODINGS = ("utf-8", "utf-8-sig", "gbk", "cp1252", "latin-1")
VECTOR_DUMMY = "VECTOR__INDEPENDENT_SIG_MSG"
STATEMENT = re.compile(
    r"^\s*(BO_TX_BU_|BO_|SG_MUL_VAL_|SG_|CM_ BU_|CM_ BO_|CM_ SG_|CM_ EV_|CM_|VAL_TABLE_|VAL_|"
    r"SIG_VALTYPE_|SIG_GROUP_|BA_DEF_DEF_|BA_DEF_|BA_|BU_)(?=[\s:\"]|$)"
)


def _die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def load_cantools(path: Path, strict: bool, keep_order: bool = True):
    """Load with cantools.

    ``keep_order=True`` keeps the signal order of the file (``sort_signals=None``), which
    is what editing and dumping want.  Anything that decodes payloads must load with
    ``keep_order=False``: with ``sort_signals=None`` cantools cannot unpack messages whose
    Intel signals are listed from high to low start bit.
    """
    try:
        import cantools
    except ImportError:
        _die("cantools is not installed. Run: pip install cantools")

    last_err = None
    for enc in ENCODINGS:
        try:
            db = cantools.database.load_file(
                str(path),
                encoding=enc,
                strict=strict,
                **({"sort_signals": None} if keep_order else {}),
            )
            return db, enc, cantools
        except UnicodeDecodeError as exc:
            last_err = exc
            continue
        except Exception as exc:  # parse / strict errors
            last_err = exc
            # encoding succeeded enough to parse; do not try other encodings
            _die(f"cantools load failed ({enc}, strict={strict}): {exc}")
    _die(f"cantools could not decode file with {ENCODINGS}: {last_err}")


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ENCODINGS:
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1")


def statement_counts(path: Path) -> Counter:
    """Count DBC statements by keyword in the raw text.

    cantools drops some statements when it loads (the Vector dummy message
    ``VECTOR__INDEPENDENT_SIG_MSG`` and its signals and comments), so a semantic diff
    cannot see them disappear; the raw counts can.
    """
    counts: Counter = Counter()
    in_namespace = False
    for line in read_text(path).splitlines():
        if line.startswith("NS_"):
            in_namespace = True
            continue
        if in_namespace:
            # The NS_ block lists bare keywords on indented lines; they are not statements.
            if line[:1] in (" ", "\t") and len(line.split()) == 1:
                continue
            in_namespace = False
        match = STATEMENT.match(line)
        if match:
            counts[match.group(1)] += 1
    if VECTOR_DUMMY in read_text(path):
        counts[VECTOR_DUMMY] = 1
    return counts


def lost_statements(old: Counter, new: Counter) -> list[str]:
    return [
        f"{key}: {old[key]} -> {new[key]}"
        for key in sorted(old)
        if new[key] < old[key]
    ]


def decode_check(path: Path) -> int:
    """Decode every message once with fixed payloads, loading with cantools' default order."""
    db, enc, _ = load_cantools(path, strict=False, keep_order=False)
    failures: list[str] = []
    checked = 0
    for msg in db.messages:
        checked += 1
        for pattern in (0x00, 0xFF, 0xA5):
            data = bytes([pattern]) * msg.length
            try:
                msg.decode(data, decode_choices=False, scaling=False)
            except Exception as exc:
                failures.append(f"{msg.name} (0x{msg.frame_id:X}) payload {data.hex()}: {exc}")
                break
    print(f"decode-check {path} encoding={enc}: {checked - len(failures)}/{checked} message(s) decode")
    for line in failures:
        print("  FAIL", line)
    return 3 if failures else 0


def load_canmatrix(path: Path):
    try:
        from canmatrix import formats
    except ImportError:
        _die("canmatrix is not installed. Run: pip install canmatrix")
    dbs = formats.loadp(str(path))
    if not dbs:
        _die("canmatrix loaded zero databases")
    return dbs


def summarize_cantools(db) -> dict:
    messages = []
    for msg in db.messages:
        messages.append(
            {
                "name": msg.name,
                "frame_id": msg.frame_id,
                "extended": bool(msg.is_extended_frame),
                "length": msg.length,
                "signals": [s.name for s in msg.signals],
            }
        )
    nodes = [n.name for n in db.nodes]
    return {
        "messages": len(db.messages),
        "nodes": nodes,
        "message_list": messages,
    }


def print_summary(label: str, summary: dict) -> None:
    print(f"{label}: {summary['messages']} message(s), {len(summary['nodes'])} node(s)")
    for msg in summary["message_list"]:
        ext = "ext" if msg["extended"] else "std"
        print(
            f"  0x{msg['frame_id']:X}({ext}) {msg['name']} "
            f"DLC={msg['length']} signals={','.join(msg['signals']) or '-'}"
        )


def run_cancompare(old: Path, new: Path) -> int:
    cmd = ["cancompare", str(old), str(new)]
    print("+", " ".join(cmd))
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True)
    except FileNotFoundError:
        print("cancompare: not installed (it ships with canmatrix); skipped")
        return 0
    out = (proc.stdout or "") + (proc.stderr or "")
    if out.strip():
        print(out.rstrip())
    else:
        print("cancompare: no textual output (exit %s)" % proc.returncode)
    return proc.returncode


def semantic_diff(old_db, new_db) -> list[str]:
    diffs: list[str] = []
    old_by = {m.name: m for m in old_db.messages}
    new_by = {m.name: m for m in new_db.messages}
    for name in sorted(set(old_by) - set(new_by)):
        diffs.append(f"- message {name}")
    for name in sorted(set(new_by) - set(old_by)):
        diffs.append(f"+ message {name}")
    for name in sorted(set(old_by) & set(new_by)):
        o, n = old_by[name], new_by[name]
        for attr in ("frame_id", "length", "is_extended_frame", "cycle_time", "comment"):
            ov, nv = getattr(o, attr), getattr(n, attr)
            if ov != nv:
                diffs.append(f"~ {name}.{attr}: {ov!r} -> {nv!r}")
        o_sigs = {s.name: s for s in o.signals}
        n_sigs = {s.name: s for s in n.signals}
        for sname in sorted(set(o_sigs) - set(n_sigs)):
            diffs.append(f"- {name}.{sname}")
        for sname in sorted(set(n_sigs) - set(o_sigs)):
            diffs.append(f"+ {name}.{sname}")
        for sname in sorted(set(o_sigs) & set(n_sigs)):
            osig, nsig = o_sigs[sname], n_sigs[sname]
            for attr in (
                "start",
                "length",
                "byte_order",
                "is_signed",
                "scale",
                "offset",
                "minimum",
                "maximum",
                "unit",
                "comment",
                "choices",
            ):
                ov, nv = getattr(osig, attr), getattr(nsig, attr)
                if ov != nv:
                    diffs.append(f"~ {name}.{sname}.{attr}: {ov!r} -> {nv!r}")
    return diffs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", help="DBC file(s). Two files with --compare.")
    parser.add_argument("--strict", action="store_true", help="cantools strict=True (default on)")
    parser.add_argument("--no-strict", action="store_true", help="cantools strict=False")
    parser.add_argument("--cross-check", action="store_true", help="also parse with canmatrix")
    parser.add_argument("--compare", action="store_true", help="semantic + cancompare of two files")
    parser.add_argument(
        "--decode-check",
        action="store_true",
        help="decode every message with fixed payloads (loads with cantools' default signal order)",
    )
    args = parser.parse_args()

    strict = not args.no_strict
    files = [Path(p) for p in args.files]
    for f in files:
        if not f.is_file():
            _die(f"not a file: {f}")

    if args.compare:
        if len(files) != 2:
            _die("--compare requires exactly two DBC files")
        old_db, old_enc, _ = load_cantools(files[0], strict)
        new_db, new_enc, _ = load_cantools(files[1], strict)
        print(f"OK cantools {files[0]} encoding={old_enc} strict={strict}")
        print_summary("old", summarize_cantools(old_db))
        print(f"OK cantools {files[1]} encoding={new_enc} strict={strict}")
        print_summary("new", summarize_cantools(new_db))
        diffs = semantic_diff(old_db, new_db)
        print(f"semantic diffs: {len(diffs)}")
        for line in diffs:
            print(" ", line)
        old_counts, new_counts = statement_counts(files[0]), statement_counts(files[1])
        print("raw statements (old -> new):")
        for key in sorted(set(old_counts) | set(new_counts)):
            marker = " " if old_counts[key] == new_counts[key] else "~"
            print(f"  {marker} {key}: {old_counts[key]} -> {new_counts[key]}")
        lost = lost_statements(old_counts, new_counts)
        if lost:
            print("WARN statements lost (cantools may not have loaded them, so the semantic diff cannot show it):")
            for line in lost:
                print(" ", line)
            if old_counts[VECTOR_DUMMY] and not new_counts[VECTOR_DUMMY]:
                print(f"  {VECTOR_DUMMY} was dropped; use Path A, or confirm the unused signals may go")
        rc = run_cancompare(files[0], files[1])
        if diffs:
            raise SystemExit(0 if rc == 0 else 0)  # diffs are expected after an edit
        raise SystemExit(0)

    if args.decode_check:
        code = 0
        for f in files:
            code = max(code, decode_check(f))
        raise SystemExit(code)

    code = 0
    for f in files:
        try:
            db, enc, _ = load_cantools(f, strict)
            print(f"OK cantools {f} encoding={enc} strict={strict}")
            print_summary("cantools", summarize_cantools(db))
        except SystemExit:
            raise
        except Exception as exc:
            print(f"FAIL cantools {f}: {exc}")
            code = 1
            continue
        if args.cross_check:
            try:
                dbs = load_canmatrix(f)
                frames = sum(len(m.frames) for m in dbs.values())
                print(f"OK canmatrix {f} databases={list(dbs)} frames={frames}")
            except SystemExit:
                raise
            except Exception as exc:
                print(f"FAIL canmatrix {f}: {exc}")
                code = 2
    raise SystemExit(code)


if __name__ == "__main__":
    main()

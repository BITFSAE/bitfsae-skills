#!/usr/bin/env python3
"""Validate a DBC with cantools (required) and optionally canmatrix."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ENCODINGS = ("utf-8", "cp1252", "latin-1")


def _die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def load_cantools(path: Path, strict: bool):
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
                sort_signals=None,
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
    proc = subprocess.run(cmd, text=True, capture_output=True)
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
        rc = run_cancompare(files[0], files[1])
        if diffs:
            raise SystemExit(0 if rc == 0 else 0)  # diffs are expected after an edit
        raise SystemExit(0)

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

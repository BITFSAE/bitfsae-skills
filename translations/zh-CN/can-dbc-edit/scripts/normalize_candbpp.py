#!/usr/bin/env python3
"""Reorder a DBC into CANdb++-friendly section order. No cantools dump."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

STARTS = (
    "BA_DEF_DEF_REL_",
    "BA_DEF_DEF_",
    "BA_DEF_REL_",
    "BA_DEF_",
    "BA_REL_",
    "BA_",
    "SIG_VALTYPE_",
    "SIGTYPE_VALTYPE_",
    "SIG_GROUP_",
    "SG_MUL_VAL_",
    "VAL_TABLE_",
    "VAL_",
    "BO_TX_BU_",
    "ENVVAR_DATA_",
    "EV_",
    "CM_",
    "BO_",
    "SG_",
    "VERSION",
    "NS_",
    "BS_",
    "BU_:",
)
LINE_KEYS = {"VERSION", "BS_", "BU_:", "BO_", "SG_"}


def starts_stmt(line: str) -> str | None:
    s = line.lstrip()
    for key in STARTS:
        if s.startswith(key):
            return key
    return None


def quotes_balanced(chunk: list[str]) -> bool:
    text = "\n".join(chunk)
    count = 0
    esc = False
    for ch in text:
        if esc:
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if ch == '"':
            count += 1
    return count % 2 == 0


def split_statements(text: str) -> list[tuple[str, list[str]]]:
    lines = text.splitlines()
    stmts: list[tuple[str, list[str]]] = []
    i = 0
    n = len(lines)
    while i < n:
        raw = lines[i]
        if not raw.strip():
            i += 1
            continue
        key = starts_stmt(raw)
        if key is None:
            if stmts:
                stmts[-1][1].append(raw)
                i += 1
                continue
            raise ValueError(f"orphan line {i + 1}: {raw!r}")
        chunk = [raw]
        if key == "NS_":
            i += 1
            while i < n:
                nxt = lines[i]
                if not nxt.strip():
                    i += 1
                    continue
                if nxt.startswith("\t") or nxt.startswith("    "):
                    chunk.append(nxt)
                    i += 1
                    continue
                break
            stmts.append((key, chunk))
            continue
        if key in LINE_KEYS:
            stmts.append((key, chunk))
            i += 1
            continue
        i += 1
        while True:
            joined = "\n".join(chunk)
            if quotes_balanced(chunk) and joined.rstrip().endswith(";"):
                break
            if i >= n:
                break
            if quotes_balanced(chunk) and starts_stmt(lines[i]):
                break
            chunk.append(lines[i])
            i += 1
        stmts.append((key, chunk))
    return stmts


def flatten_comment(chunk: list[str]) -> list[str]:
    text = "\n".join(chunk)
    out: list[str] = []
    in_quote = False
    esc = False
    for ch in text:
        if esc:
            out.append(ch)
            esc = False
            continue
        if ch == "\\" and in_quote:
            out.append(ch)
            esc = True
            continue
        if ch == '"':
            in_quote = not in_quote
            out.append(ch)
            continue
        if in_quote and ch in "\r\n":
            if out and out[-1] != " ":
                out.append(" ")
            continue
        out.append(ch)
    line = "".join(out)
    while "  " in line:
        line = line.replace("  ", " ")
    return [line.rstrip()]


def space_semi(chunk: list[str]) -> list[str]:
    last = chunk[-1].rstrip()
    if last.endswith(";") and not last.endswith(" ;"):
        return chunk[:-1] + [last[:-1].rstrip() + " ;"]
    return chunk


def render(text: str) -> str:
    stmts = split_statements(text)
    bos: list[list[str]] = []
    cms: list[list[str]] = []
    vals: list[list[str]] = []
    sigs: list[list[str]] = []
    ba_def: list[list[str]] = []
    ba_def_def: list[list[str]] = []
    ba: list[list[str]] = []
    others: list[list[str]] = []
    current_bo: list[str] | None = None
    version = ns = bs = bu = None

    for key, chunk in stmts:
        if key == "VERSION":
            version = chunk
        elif key == "NS_":
            ns = chunk
        elif key == "BS_":
            bs = chunk
        elif key == "BU_:":
            bu = chunk
        elif key == "BO_":
            current_bo = list(chunk)
            bos.append(current_bo)
        elif key == "SG_":
            if current_bo is None:
                raise ValueError(f"SG_ without BO_: {chunk}")
            current_bo.extend(chunk)
        elif key == "CM_":
            current_bo = None
            cms.append(flatten_comment(chunk))
        elif key == "VAL_":
            current_bo = None
            vals.append(space_semi(list(chunk)))
        elif key == "SIG_VALTYPE_":
            current_bo = None
            sigs.append(space_semi(list(chunk)))
        elif key == "BA_DEF_":
            current_bo = None
            ba_def.append(list(chunk))
        elif key == "BA_DEF_DEF_":
            current_bo = None
            ba_def_def.append(list(chunk))
        elif key == "BA_":
            current_bo = None
            ba.append(list(chunk))
        else:
            current_bo = None
            others.append(list(chunk))

    if bu and "Vector__XXX" in text and "Vector__XXX" not in bu[0]:
        bu[0] = bu[0].rstrip() + " Vector__XXX"

    out: list[str] = []
    if version:
        out.extend(version)
        out.append("")
    if ns:
        out.extend(ns)
        out.append("")
    if bs:
        out.extend(bs)
        out.append("")
    else:
        out.extend(["BS_:", ""])
    if bu:
        out.extend(bu)
        out.append("")
    out.append("")
    for block in bos:
        out.extend(block)
        out.append("")
    out.append("")
    for block in cms:
        out.extend(block)
    if cms:
        out.append("")
    for block in ba_def:
        out.extend(block)
    for block in ba_def_def:
        out.extend(block)
    if ba_def or ba_def_def:
        out.append("")
    for block in ba:
        out.extend(block)
    if ba:
        out.append("")
    for block in others:
        out.extend(block)
    if others:
        out.append("")
    for block in vals:
        out.extend(block)
    if vals:
        out.append("")
    for block in sigs:
        out.extend(block)
    if sigs:
        out.append("")
    return "\r\n".join(out) + "\r\n"


def write_variants(body: str, dest_stem: Path) -> dict[str, Path]:
    parent = dest_stem.parent
    stem = dest_stem.name
    paths = {
        "utf8": parent / f"{stem}.dbc",
        "gbk": parent / f"{stem}_gbk.dbc",
        "utf8bom": parent / f"{stem}_utf8bom.dbc",
    }
    paths["utf8"].write_bytes(body.encode("utf-8"))
    paths["utf8bom"].write_bytes(b"\xef\xbb\xbf" + body.encode("utf-8"))
    try:
        paths["gbk"].write_bytes(body.encode("gbk"))
    except UnicodeEncodeError as exc:
        raise SystemExit(f"GBK cannot encode this file: {exc}") from exc
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src")
    parser.add_argument("dest_stem", help="output prefix without encoding suffix")
    args = parser.parse_args()
    src = Path(args.src)
    text = src.read_text("utf-8")
    body = render(text)
    paths = write_variants(body, Path(args.dest_stem))
    for label, path in paths.items():
        print(f"{label}\t{path}\t{path.stat().st_size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

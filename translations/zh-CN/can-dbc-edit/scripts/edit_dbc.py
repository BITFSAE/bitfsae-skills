#!/usr/bin/env python3
"""Apply structured JSON operations to a DBC via cantools, then dump and re-parse."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_dbc import load_cantools

SIGNAL_SCALAR_FIELDS = {
    "scale",
    "offset",
    "minimum",
    "maximum",
    "unit",
    "comment",
    "is_signed",
    "is_float",
}


def _die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def _msg(db, name: str):
    try:
        return db.get_message_by_name(name)
    except KeyError:
        _die(f"unknown message: {name}")


def _sig(msg, name: str):
    try:
        return msg.get_signal_by_name(name)
    except KeyError:
        _die(f"unknown signal {msg.name}.{name}")


def _byte_order(value: str) -> str:
    mapping = {
        "little_endian": "little_endian",
        "intel": "little_endian",
        "@1": "little_endian",
        "big_endian": "big_endian",
        "motorola": "big_endian",
        "@0": "big_endian",
    }
    key = str(value).lower()
    if key not in mapping:
        _die(f"byte_order must be little_endian/intel/@1 or big_endian/motorola/@0, got {value!r}")
    return mapping[key]


def _choices(raw) -> dict[int, str]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        _die("choices must be an object of raw-value -> label")
    out = {}
    for k, v in raw.items():
        out[int(k)] = str(v)
    return out


def apply_op(db, op: dict) -> str:
    if not isinstance(op, dict) or "op" not in op:
        _die(f"invalid op: {op!r}")
    kind = op["op"]

    if kind == "set_signal":
        msg = _msg(db, op["message"])
        sig = _sig(msg, op["signal"])
        fields = op.get("fields") or {}
        extra = set(fields) - SIGNAL_SCALAR_FIELDS
        if extra:
            _die(f"set_signal rejected fields {sorted(extra)}. Use set_layout/rename_signal.")
        changes = []
        for key, val in fields.items():
            old = getattr(sig, key)
            setattr(sig, key, val)
            changes.append(f"{key}:{old!r}->{val!r}")
        return f"set_signal {msg.name}.{sig.name} " + ", ".join(changes)

    if kind == "set_choices":
        msg = _msg(db, op["message"])
        sig = _sig(msg, op["signal"])
        old = dict(sig.choices) if sig.choices else {}
        sig.choices = _choices(op.get("choices") or {})
        return f"set_choices {msg.name}.{sig.name} {old} -> {sig.choices}"

    if kind == "set_cycle_time":
        msg = _msg(db, op["message"])
        old = msg.cycle_time
        msg.cycle_time = op.get("cycle_time")
        return f"set_cycle_time {msg.name} {old} -> {msg.cycle_time}"

    if kind == "set_comment":
        scope = op.get("scope")
        comment = op.get("comment")
        if scope == "database":
            old = db.version
            # Database comment lives on dbc specifics; set message-level if missing
            if hasattr(db, "dbc") and db.dbc is not None:
                pass
            db.comment = comment if hasattr(db, "comment") else comment
            try:
                old = db.comment
            except Exception:
                old = None
            if hasattr(db, "comment"):
                db.comment = comment
            return f"set_comment database {old!r} -> {comment!r}"
        if scope == "message":
            msg = _msg(db, op["message"])
            old = msg.comment
            msg.comment = comment
            return f"set_comment message {msg.name} {old!r} -> {comment!r}"
        if scope == "signal":
            msg = _msg(db, op["message"])
            sig = _sig(msg, op["signal"])
            old = sig.comment
            sig.comment = comment
            return f"set_comment signal {msg.name}.{sig.name} {old!r} -> {comment!r}"
        _die("set_comment scope must be database, message, or signal")

    if kind == "rename_signal":
        msg = _msg(db, op["message"])
        sig = _sig(msg, op["signal"])
        new_name = op["new_name"]
        old = sig.name
        sig.name = new_name
        return f"rename_signal {msg.name}.{old} -> {new_name}"

    if kind == "rename_message":
        msg = _msg(db, op["message"])
        old = msg.name
        msg.name = op["new_name"]
        return f"rename_message {old} -> {msg.name}"

    if kind == "set_frame_id":
        msg = _msg(db, op["message"])
        frame_id = op["frame_id"]
        if isinstance(frame_id, str):
            if frame_id.lower().startswith("0x"):
                _die("frame_id must be an integer, not a hex string")
            frame_id = int(frame_id)
        old = (msg.frame_id, msg.is_extended_frame)
        msg.frame_id = int(frame_id)
        if "is_extended_frame" in op:
            msg.is_extended_frame = bool(op["is_extended_frame"])
        return f"set_frame_id {msg.name} {old} -> {(msg.frame_id, msg.is_extended_frame)}"

    if kind == "set_layout":
        msg = _msg(db, op["message"])
        sig = _sig(msg, op["signal"])
        parts = []
        if "start" in op:
            parts.append(f"start {sig.start}->{op['start']}")
            sig.start = int(op["start"])
        if "length" in op:
            parts.append(f"length {sig.length}->{op['length']}")
            sig.length = int(op["length"])
        if "byte_order" in op:
            order = _byte_order(op["byte_order"])
            parts.append(f"byte_order {sig.byte_order}->{order}")
            sig.byte_order = order
        if not parts:
            _die("set_layout needs start, length, and/or byte_order")
        return f"set_layout {msg.name}.{sig.name} " + ", ".join(parts)

    if kind == "add_signal":
        from cantools.database.can.signal import Signal
        from cantools.database.conversion import BaseConversion

        msg = _msg(db, op["message"])
        try:
            msg.get_signal_by_name(op["name"])
            _die(f"signal already exists: {msg.name}.{op['name']}")
        except KeyError:
            pass
        conv = BaseConversion.factory(
            scale=float(op.get("scale", 1)),
            offset=float(op.get("offset", 0)),
            choices=_choices(op["choices"]) if op.get("choices") else None,
            is_float=bool(op.get("is_float", False)),
        )
        sig = Signal(
            name=op["name"],
            start=int(op["start"]),
            length=int(op["length"]),
            byte_order=_byte_order(op.get("byte_order", "little_endian")),
            is_signed=bool(op.get("is_signed", False)),
            conversion=conv,
            minimum=op.get("minimum"),
            maximum=op.get("maximum"),
            unit=op.get("unit"),
            comment=op.get("comment"),
            receivers=list(op.get("receivers") or []),
        )
        msg.signals.append(sig)
        return f"add_signal {msg.name}.{sig.name} start={sig.start} len={sig.length}"

    if kind == "delete_signal":
        msg = _msg(db, op["message"])
        sig = _sig(msg, op["signal"])
        msg.signals.remove(sig)
        return f"delete_signal {msg.name}.{sig.name}"

    if kind == "add_message":
        from cantools.database.can.message import Message

        name = op["name"]
        try:
            db.get_message_by_name(name)
            _die(f"message already exists: {name}")
        except KeyError:
            pass
        frame_id = op["frame_id"]
        if isinstance(frame_id, str) and frame_id.lower().startswith("0x"):
            _die("frame_id must be an integer, not a hex string")
        msg = Message(
            frame_id=int(frame_id),
            name=name,
            length=int(op.get("length", 8)),
            signals=[],
            comment=op.get("comment"),
            senders=list(op.get("senders") or []),
            cycle_time=op.get("cycle_time"),
            is_extended_frame=bool(op.get("is_extended_frame", False)),
            is_fd=bool(op.get("is_fd", False)),
            strict=False,
            sort_signals=None,
        )
        db.messages.append(msg)
        return f"add_message {name} id={msg.frame_id} dlc={msg.length}"

    if kind == "delete_message":
        msg = _msg(db, op["message"])
        db.messages.remove(msg)
        return f"delete_message {msg.name}"

    _die(f"unknown op: {kind}")


def dump_dbc(db, path: Path, encoding: str, cantools_mod) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cantools_mod.database.dump_file(
        db,
        str(path),
        encoding=encoding,
        sort_signals=None,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dbc")
    parser.add_argument("output_dbc")
    parser.add_argument("ops_json")
    parser.add_argument("--no-strict-in", action="store_true", help="allow sloppy source parse")
    args = parser.parse_args()

    in_path = Path(args.input_dbc)
    out_path = Path(args.output_dbc)
    ops_path = Path(args.ops_json)
    if not in_path.is_file():
        _die(f"missing input: {in_path}")
    if not ops_path.is_file():
        _die(f"missing ops json: {ops_path}")

    spec = json.loads(ops_path.read_text(encoding="utf-8"))
    ops = spec.get("ops", spec if isinstance(spec, list) else None)
    if not isinstance(ops, list) or not ops:
        _die("ops JSON must contain a non-empty 'ops' array")

    db, encoding, cantools_mod = load_cantools(in_path, strict=not args.no_strict_in)
    print(f"loaded {in_path} encoding={encoding} messages={len(db.messages)}")

    for i, op in enumerate(ops, 1):
        summary = apply_op(db, op)
        print(f"[{i}/{len(ops)}] {summary}")

    try:
        db.refresh()
    except Exception as exc:
        print(f"WARN db.refresh: {exc}")

    dump_dbc(db, out_path, encoding, cantools_mod)
    print(f"wrote {out_path}")

    # Must parse back.
    load_cantools(out_path, strict=True)
    print(f"OK re-parse strict {out_path}")


if __name__ == "__main__":
    main()

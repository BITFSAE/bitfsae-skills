#!/usr/bin/env python3
"""Create deterministic ZIP bundles for OpenAI Skills API uploads."""

from __future__ import annotations

import argparse
import stat
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
DEFAULT_OUTPUT_DIR = ROOT / "dist"
IGNORED_NAMES = {".DS_Store", "__pycache__"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}
FORBIDDEN_NAMES = {".env"}
FORBIDDEN_SUFFIXES = {".key", ".p12", ".pem", ".pfx"}
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Package one or more skill directories as ZIP files."
    )
    parser.add_argument(
        "skills",
        nargs="*",
        help="Skill names to package; omit to package every skill.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory (default: repository dist/).",
    )
    return parser.parse_args()


def discover_skills(requested: list[str]) -> list[Path]:
    available = {
        path.name: path
        for path in SKILLS_DIR.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }
    if not requested:
        return [available[name] for name in sorted(available)]

    missing = sorted(set(requested) - available.keys())
    if missing:
        names = ", ".join(missing)
        raise ValueError(f"unknown skill(s): {names}")
    return [available[name] for name in requested]


def package_skill(skill_dir: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{skill_dir.name}.zip"

    files: list[Path] = []
    for path in skill_dir.rglob("*"):
        relative_path = path.relative_to(skill_dir)
        if any(part in IGNORED_NAMES for part in relative_path.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"symlinks are not allowed in bundles: {path}")
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            raise ValueError(f"credential files are not allowed in bundles: {path}")
        if path.is_file() and path.suffix not in IGNORED_SUFFIXES:
            files.append(path)

    if not files:
        raise ValueError(f"skill has no packageable files: {skill_dir.name}")

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            relative = path.relative_to(skill_dir).as_posix()
            info = zipfile.ZipInfo(relative, ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, path.read_bytes())

    return output_path


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.expanduser().resolve()
    try:
        skill_dirs = discover_skills(args.skills)
        for skill_dir in skill_dirs:
            output_path = package_skill(skill_dir, output_dir)
            display_path = (
                output_path.relative_to(ROOT)
                if output_path.is_relative_to(ROOT)
                else output_path
            )
            print(display_path)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

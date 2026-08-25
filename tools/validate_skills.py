#!/usr/bin/env python3
"""Validate the structure and public boundary of all skills in this repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"(?<!!)\[[^]]*]\(([^)]+)\)")
FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
SKILLS_SH_CONFIG = ROOT / "skills.sh.json"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_links(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for target in LINK_PATTERN.findall(text):
        clean = unquote(target.split("#", 1)[0].strip())
        if not clean or "://" in clean or clean.startswith("mailto:"):
            continue
        if not (path.parent / clean).resolve().exists():
            fail(f"{path.relative_to(ROOT)} contains a missing link: {target}")


def validate_skill(skill_dir: Path) -> None:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        fail(f"{skill_dir.relative_to(ROOT)} is missing SKILL.md")

    text = skill_file.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        fail(f"{skill_file.relative_to(ROOT)} has invalid frontmatter boundaries")

    metadata = yaml.safe_load(match.group(1))
    if not isinstance(metadata, dict) or set(metadata) != {"name", "description"}:
        fail(f"{skill_file.relative_to(ROOT)} frontmatter must contain only name and description")
    name = metadata.get("name")
    description = metadata.get("description")
    if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
        fail(f"{skill_file.relative_to(ROOT)} has an invalid skill name")
    if name != skill_dir.name:
        fail(f"skill folder {skill_dir.name} does not match name {name}")
    if not isinstance(description, str) or not description.strip():
        fail(f"{skill_file.relative_to(ROOT)} has an empty description")
    if len(text.splitlines()) > 500:
        fail(f"{skill_file.relative_to(ROOT)} exceeds 500 lines; move details to references")

    validate_links(skill_file)
    for reference in (skill_dir / "references").glob("*.md") if (skill_dir / "references").is_dir() else ():
        validate_links(reference)

    agent_file = skill_dir / "agents/openai.yaml"
    if agent_file.is_file():
        agent = yaml.safe_load(agent_file.read_text(encoding="utf-8"))
        interface = agent.get("interface") if isinstance(agent, dict) else None
        if not isinstance(interface, dict):
            fail(f"{agent_file.relative_to(ROOT)} is missing interface metadata")
        default_prompt = interface.get("default_prompt", "")
        if f"${name}" not in default_prompt:
            fail(f"{agent_file.relative_to(ROOT)} default_prompt must mention ${name}")

    print(f"OK: {name}")


def validate_public_boundary() -> None:
    forbidden_suffixes = {".key", ".pem", ".p12", ".pfx"}
    private_key_marker = "-----BEGIN " + "PRIVATE KEY-----"
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.name == ".env" or path.suffix.lower() in forbidden_suffixes:
            fail(f"credential file is not allowed: {path.relative_to(ROOT)}")
        if path.suffix.lower() not in {".json", ".md", ".py", ".yaml", ".yml"}:
            continue
        if private_key_marker in path.read_text(encoding="utf-8"):
            fail(f"private key content found in {path.relative_to(ROOT)}")
    print("OK: public repository boundary")


def validate_skills_sh(skill_names: set[str]) -> None:
    if not SKILLS_SH_CONFIG.is_file():
        return
    try:
        config = json.loads(SKILLS_SH_CONFIG.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        fail(f"skills.sh.json is invalid JSON: {error}")

    groupings = config.get("groupings") if isinstance(config, dict) else None
    if not isinstance(groupings, list) or not groupings:
        fail("skills.sh.json must contain at least one grouping")
    for index, grouping in enumerate(groupings, start=1):
        if not isinstance(grouping, dict):
            fail(f"skills.sh.json grouping {index} must be an object")
        title = grouping.get("title")
        names = grouping.get("skills")
        if not isinstance(title, str) or not title.strip():
            fail(f"skills.sh.json grouping {index} has an empty title")
        if not isinstance(names, list) or not names:
            fail(f"skills.sh.json grouping {index} has no skills")
        unknown = sorted(name for name in names if name not in skill_names)
        if unknown:
            fail(
                f"skills.sh.json grouping {index} references unknown skills: "
                + ", ".join(unknown)
            )
    print("OK: skills.sh.json")


def main() -> None:
    if not SKILLS_DIR.is_dir():
        fail("skills directory is missing")
    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
    if not skill_dirs:
        fail("no skills found")
    for skill_dir in skill_dirs:
        validate_skill(skill_dir)
    validate_skills_sh({path.name for path in skill_dirs})
    for path in ROOT.glob("*.md"):
        validate_links(path)
    validate_public_boundary()
    print(f"Validated {len(skill_dirs)} skill(s)")


if __name__ == "__main__":
    main()

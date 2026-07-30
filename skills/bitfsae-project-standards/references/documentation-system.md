# Documentation System

## Contents

1. Document ownership
2. README
3. AI instruction files
4. Changelog and TODO
5. External interface documents
6. Configuration documents
7. Module and design documents
8. Hardware and build documents
9. Writing and maintenance rules

## 1. Document Ownership

Each detailed fact has one primary owner. Summarize and link from the README; do not maintain independent copies.

| Information | Preferred owner |
| --- | --- |
| Project purpose, quick start, document index | `README.md` |
| AI editing constraints | `AGENTS.md`, `CLAUDE.md` |
| Released changes and pending work | `CHANGELOG.md` |
| Public protocol or API | Dedicated interface document and schema |
| Frequently changed values | Configuration document and named code definitions |
| Module state, algorithm, failure behavior | Module document |
| Pins, nets, electrical assumptions | Hardware document and design files |
| Build, flash, test, debug | Build/development document |

## 2. README

Write for a new teammate deciding what the project is and where to start. Prefer this order when applicable:

1. one-paragraph purpose and scope;
2. document index;
3. major capabilities and exclusions;
4. concise hardware/runtime overview;
5. public interface summary with links;
6. source tree or major modules;
7. shortest verified build path;
8. safety or operational warnings.

Keep low-level register values, full protocol layouts, long algorithms, and exhaustive troubleshooting in dedicated documents.

## 3. AI Instruction Files

Use imperative rules for how an AI should edit and verify the repository. Include only stable instructions:

- generated-file editing limits;
- where new logic belongs;
- third-party code policy;
- required build/test commands;
- documentation synchronization rules;
- comment language and clarity requirements;
- repository-specific safety constraints.

Do not include project overviews, mutable hardware values, CAN message tables, file inventories, or facts owned by other documents. Keep `AGENTS.md` and `CLAUDE.md` aligned when both exist. BITFSAE `AGENTS.md` must retain `DO NOT send optional commentary` unless explicitly removed.

## 4. Changelog and TODO

Use a readable reverse-chronological `CHANGELOG.md`:

- `未发布` for work not yet released;
- `未发布/待办` for concrete, still-needed work;
- dated sections for completed behavior, interfaces, build changes, fixes, and migration notes.

Record outcomes and compatibility impact, not every commit. Do not claim an untested feature is complete. Remove `todo.md` only when it duplicates the changelog; keep it when it contains substantial scheduling or ownership information that does not belong in release history.

## 5. External Interface Documents

Write as contracts for producers and consumers. Compact overview → exact tables → error behavior → verified examples. Keep interpretation separate from raw layout.

For each field include: name, offset, width, type, byte order, scale, offset, unit, range, invalid value, and meaning. State timing, reset, retry, sequence, persistence, and version compatibility. Use the project's implementation language for examples.

Keep DBC, OpenAPI, JSON Schema, protobuf, public headers, or similar machine-readable definitions synchronized with prose. Note when a schema contains provisional names requiring upstream verification.

## 6. Configuration Documents

Optimize for safe modification. Use a table with:

- setting and current value;
- code symbol or generator location;
- unit and valid range;
- behavior or hardware affected;
- documents, tests, calibration, or consumers that must also change.

Separate generated peripheral configuration, compile-time policy defaults, runtime commands, persistent settings, calibration values, and secrets. State reboot/reset behavior. Do not expose real credentials or private keys.

## 7. Module and Design Documents

Create one when a module has a state machine, control policy, concurrency, calibration, safety fallback, non-obvious algorithm, or multiple external interactions.

Suggested structure:

1. responsibility and boundaries;
2. inputs, outputs, and dependencies;
3. states or processing sequence;
4. timing and concurrency;
5. configuration;
6. faults and fallback behavior;
7. public functions or integration points;
8. verification and test cases.

Use a diagram only when it explains relationships or state changes more clearly than a short list. Avoid restating every function body.

## 8. Hardware and Build Documents

Hardware documents: map logical functions to pins, nets, peripherals, electrical levels, polarity, pull resistors, isolation, sensor addresses, and calibration assumptions. Distinguish schematic facts from software expectations and unverified board behavior.

Build documents: prerequisites, exact supported commands, output paths, flash/debug entry points, generator workflow, and regeneration checks. Prefer the maintained build system. Keep fallback build paths only when verified and useful.

## 9. Writing and Maintenance Rules

- Match structure to purpose: README navigates, interface docs are exact, configuration docs are task-oriented, module docs explain behavior, changelogs summarize change.
- Lead with the result or behavior. Define abbreviations once. Put units next to values.
- Prefer tables for exact field mappings and configuration. Prefer prose for reasons and interactions.
- Remove stale history from current-state documents; keep it in the changelog or version control.
- Avoid exaggerated claims, generic teaching, repeated warnings, and text that does not help a teammate operate or modify the project.
- During every relevant code change, update the owning document in the same work item.

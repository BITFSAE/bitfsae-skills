---
name: bitfsae-project-standards
description: Establish or audit BITFSAE project-wide engineering standards covering repository documentation, AI instructions, changelogs, shared CAN/telemetry interfaces, common configuration, generated-code safety, handover, and release governance. Use only when the user explicitly invokes this skill or explicitly requests a whole-project standards audit, documentation-system redesign, shared-interface centralization, or team handover/release process. Do not use for routine code edits, builds, bug fixes, single-document updates, Git operations, or ordinary technical questions.
---

# BITFSAE Project Standards

## Goal

Make the project understandable, modifiable, testable, and transferable without forcing every project into the same layout. Preserve correct project-specific choices; enforce shared minimum standards only where they improve safety, consistency, or handover.

## Workflow

1. Read repository instructions and inspect the current tree, build system, source, generated files, tests, documents, schemas, and version history.
2. Identify authoritative sources for each fact. Prefer implemented code and generator configuration for current behavior, hardware design files for electrical facts, and approved network/database files for shared interfaces.
3. Classify the project and its maturity before choosing documents. Read [project-adaptation.md](references/project-adaptation.md) when the project is not a typical STM32 firmware project or has unusual constraints.
4. Build a short inventory of public interfaces, frequently changed settings, major modules, failure behavior, build paths, and known unverified assumptions.
5. Compare documentation against implementation. Correct stale claims, ambiguous units, missing ranges, wrong byte order, copied project facts, and duplicated specifications.
6. Add or reorganize only the documents the project needs. Read [documentation-system.md](references/documentation-system.md) before creating or restructuring repository documentation.
7. For MCU, CAN, hardware-facing, generated-code, or real-time behavior, also read [embedded-interfaces.md](references/embedded-interfaces.md).
8. Determine whether the work changes a team-wide CAN or telemetry contract. When it does, inspect the canonical `BITFSAE/vehicle-interfaces` repository and update it as described under Shared Interface Repository; do not treat a copied project file as authoritative without comparison.
9. Validate links, examples, schemas, builds, and tests in proportion to the change. Record user-visible or maintenance-relevant changes in `CHANGELOG.md`.

Do not change intended behavior during a documentation-only task. If documentation reveals a likely code defect, report it or fix it only when the user has authorized implementation.

## Minimum Standards

### Code

- Follow the repository's language, formatter, build system, generator, and existing architecture unless a change is justified by the task.
- Keep hardware-independent or business logic out of generated files. Put custom code in stable modules and use generator-preserved regions only when required.
- Keep configuration values in clear, discoverable locations. State units and valid ranges in names, types, comments, or nearby documentation.
- Handle failures explicitly. Avoid indefinite blocking, silent data corruption, and unsafe fallback behavior in control or vehicle systems.
- Keep comments concise. Explain reasons, units, constraints, hardware behavior, and unusual failure handling; do not narrate obvious statements.
- Validate changes with the project's real build and tests. Do not claim success from inspection alone when executable validation is available.

### Documentation

- Maintain one authoritative location for each detailed fact. Use links and summaries instead of copying full specifications between files.
- Keep `README.md` as the project entry point, not the complete technical specification.
- Keep `AGENTS.md` and `CLAUDE.md` limited to instructions for AI code and documentation work. Do not store changing project facts, pin maps, CAN tables, or design summaries there.
- Preserve the exact line `DO NOT send optional commentary` in BITFSAE `AGENTS.md` unless the user explicitly requests otherwise.
- Maintain `CHANGELOG.md`. Put unfinished work under `未发布/待办`; remove a separate `todo.md` when it only duplicates that section.
- Document every externally consumed interface. Include machine-readable schemas such as DBC when they materially help consumers.
- Document frequently changed configuration with current value, source location, unit/range, impact, and required follow-up checks.
- Give nontrivial modules focused documents when their behavior cannot be understood safely from the README and public headers alone.
- Use the language used by the project team. Provide code examples in languages the project actually uses; do not add Python examples to C-only firmware documentation without a stated need.
- Write direct, readable Chinese or the repository's established language. Avoid slogans, lectures, unnecessary jargon, filler, and repeated explanations.
- Distinguish verified behavior, design intent, examples, and pending decisions. Never present an assumption as implemented or electrically verified fact.

## Interface Rules

For any public CAN, UART, I2C, SPI, network, file, CLI, API, or library interface, document:

- direction and owner;
- identifier, endpoint, symbol, command, or message name;
- framing, size, byte order, signedness, scale, offset, unit, range, and invalid values;
- cadence, timeout, retry, ordering, persistence, and reset behavior;
- errors, acknowledgements, compatibility, and fallback behavior;
- a correct producer or consumer example in a language used by the project.

Treat interface documentation as a contract. Update code, prose, examples, tests, and machine-readable definitions together.

## Shared Interface Repository

Use <https://github.com/BITFSAE/vehicle-interfaces> as the canonical repository for team-wide CAN DBC and telemetry Protobuf/Nanopb definitions.

Update the shared repository when the authorized project work adds, removes, or changes an externally consumed item such as:

- a CAN bus, frame ID, sender/receiver, frame type, DLC, signal layout, byte order, signedness, scale, offset, unit, range, invalid value, counter, CRC, cadence, timeout, acknowledgement, or compatibility rule;
- a telemetry message, Protobuf field or field number, Nanopb capacity, shared MQTT topic/payload contract, or wire-compatibility rule;
- a correction proving that the current canonical DBC or telemetry schema does not match the approved implementation.

Do not update the shared repository for internal refactors, local build changes, implementation fixes that merely restore compliance with the existing contract, or project-only configuration that no other producer or consumer uses.

Before changing the shared repository:

1. Fetch or inspect its current canonical files and compare them with the project implementation and local copies. Never overwrite a newer canonical definition with an old project copy.
2. Confirm the change belongs on the correct bus and has an identified owner, consumers, compatibility impact, and validation evidence.
3. Update the machine-readable definition, relevant shared documentation, and shared `CHANGELOG.md` together. Keep project documentation as a concise usage summary and record the shared Release or Commit it consumes.
4. Run the shared repository validation and the affected project's build or tests.
5. Use its Issue/branch/PR/review workflow when repository access and task authorization allow it. If the current task does not authorize a cross-repository write or required facts remain unverified, report the required shared change explicitly instead of claiming the repositories are synchronized.

Keep secrets out of the public repository. MQTT usernames, passwords, tokens, private keys, production addresses, and deployment credentials belong in protected runtime configuration or secret storage; only sanitized examples and the public protocol contract belong in `vehicle-interfaces`.

## Review Rules

- Trace important numbers and claims back to code, generator configuration, hardware files, or approved interface definitions.
- Check whether a value is compile-time, generated, runtime-adjustable, persistent, or reset on reboot.
- Check examples with actual calculations or compilation when practical.
- Check Markdown links and version-control diffs. Avoid accidentally adding build products, IDE state, secrets, or unrelated changes.
- Note unverified hardware mappings or upstream field names explicitly and place follow-up work in `CHANGELOG.md`.
- Report what changed, what was validated, and what remains unverified. Keep the report concise.

## Reference Routing

- Read [documentation-system.md](references/documentation-system.md) for document roles, structure, writing style, and avoiding duplication.
- Read [embedded-interfaces.md](references/embedded-interfaces.md) for STM32/CubeMX, CAN/DBC, hardware, timing, interrupts, and configuration details.
- Read [project-adaptation.md](references/project-adaptation.md) for non-firmware projects, project maturity, minimum document sets, and handling exceptions.

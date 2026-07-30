---
name: bitfsae-project-standards
description: Establish or audit BITFSAE project-wide engineering standards covering repository documentation, AI instructions, changelogs, shared CAN/telemetry interfaces, common configuration, generated-code safety, handover, and release governance. Use only when the user explicitly invokes this skill or explicitly requests a whole-project standards audit, documentation-system redesign, shared-interface centralization, or team handover/release process. Do not use for routine code edits, builds, bug fixes, single-document updates, Git operations, or ordinary technical questions.
---

# BITFSAE Project Standards

## Goal

Make the project understandable, modifiable, testable, and transferable without forcing a uniform layout. Preserve correct project-specific choices; enforce shared minimum standards only where they improve safety, consistency, or handover.

## Workflow

1. Read repository instructions and inspect the current tree, build system, source, generated files, tests, documents, schemas, and version history.
2. Identify authoritative sources for each fact. Current behavior → implementation code and generator configuration; electrical facts → hardware design files; shared interfaces → approved network/database files.
3. Classify the project and its maturity. Read [project-adaptation.md](references/project-adaptation.md) when the project is not a typical STM32 firmware project or has unusual constraints.
4. Build a short inventory of public interfaces, frequently changed settings, major modules, failure behavior, build paths, and known unverified assumptions.
5. Compare documentation against implementation. Correct stale claims, ambiguous units, missing ranges, wrong byte order, copied project facts, and duplicated specifications.
6. Add or reorganize only the documents the project needs. Read [documentation-system.md](references/documentation-system.md) first.
7. For MCU, CAN, hardware interfaces, generated code, or real-time behavior, also read [embedded-interfaces.md](references/embedded-interfaces.md).
8. If the work changes a team-wide CAN or telemetry contract, check the canonical `BITFSAE/vehicle-interfaces` repository and update it per the Shared Interface Repository section; do not treat a local copy as authoritative without comparison.
9. Validate links, examples, schemas, builds, and tests in proportion to the change. Record user-visible or maintenance-relevant changes in `CHANGELOG.md`.

Do not change intended behavior during a documentation-only task. If documentation reveals a likely code defect, report it or fix it only when authorized.

## Minimum Standards

### Code

- Follow the repository's language, formatter, build system, generator, and existing architecture unless a change is justified.
- Keep hardware-independent and business logic out of generated files. Put custom code in stable modules; use generator-preserved regions only when necessary.
- Put configuration values in clear, discoverable locations. State units and valid ranges in names, types, comments, or nearby documentation.
- Handle failures explicitly. Avoid indefinite blocking, silent data corruption, and unsafe fallback behavior, especially in control and vehicle systems.
- Keep comments concise. Explain reasons, units, constraints, hardware behavior, and unusual failure handling; do not narrate obvious statements.
- Validate changes with the project's real build and tests. Do not claim success from inspection alone when executable validation is available.

### Documentation

- Maintain one authoritative location for each detailed fact. Use links and summaries instead of copying full specifications between files.
- `README.md` is the project entry point, not the complete technical specification. `AGENTS.md` and `CLAUDE.md` are for AI editing instructions only; do not store changing project facts there.
- Preserve `DO NOT send optional commentary` in BITFSAE `AGENTS.md` unless explicitly removed by the user.
- Maintain `CHANGELOG.md`. Put unfinished work under `未发布/待办`. Remove `todo.md` only when it merely duplicates the changelog — keep it when it contains substantial planning, scheduling, or ownership information.
- External interfaces, frequently changed configuration, and nontrivial modules all require documentation. See [documentation-system.md](references/documentation-system.md) for detailed requirements.
- Write documentation and code examples in the team's language. Do not add examples in unrelated languages to C-only firmware documentation.
- Distinguish verified behavior, design intent, examples, and pending decisions. Never present an assumption as implemented or verified fact.
- Be direct and readable. Avoid slogans, lectures, unnecessary jargon, filler, and repetition.

## Interface Rules

For any public CAN, UART, I2C, SPI, network, file, CLI, API, or library interface, document:

- direction and owner;
- identifier, endpoint, or message name;
- framing, byte order, signedness, scale, offset, unit, range, and invalid values;
- cadence, timeout, retry, ordering, persistence, and reset behavior;
- errors, acknowledgements, compatibility, and fallback behavior;
- a correct producer or consumer example in the project's language.

Interface documentation is a contract. Update code, prose, examples, tests, and machine-readable definitions together. See [documentation-system.md](references/documentation-system.md) §5 and [embedded-interfaces.md](references/embedded-interfaces.md) §3–§4 for detailed specifications.

## Shared Interface Repository

Use <https://github.com/BITFSAE/vehicle-interfaces> as the canonical repository for team-wide CAN DBC and telemetry Protobuf/Nanopb definitions.

Update the shared repository when work adds, removes, or changes externally consumed CAN frames/signals/layouts or telemetry messages/fields/compatibility rules. See [embedded-interfaces.md](references/embedded-interfaces.md) §3 for specific boundaries. Do not update for internal refactors, local build changes, compliance-restoring fixes, or project-only configuration.

Before changing:

1. Fetch the authoritative files and compare with the project implementation and local copies. Never overwrite a newer canonical definition with an old project copy.
2. Confirm the change belongs on the correct bus and has an identified owner, consumers, compatibility impact, and validation evidence.
3. Update the machine-readable definition, shared documentation, and shared `CHANGELOG.md` together.
4. Run shared repository validation and affected project builds/tests.
5. Use the Issue/branch/PR/review workflow when authorized. If cross-repository writes are not authorized or facts remain unverified, report the required change explicitly rather than claiming synchronization.

Keep secrets out of public repositories.

## Review Rules

- Trace important numbers and claims back to code, generator configuration, hardware files, or approved interface definitions.
- Check whether a value is compile-time, generated, runtime-adjustable, persistent, or reset on reboot.
- Verify examples with actual calculations or compilation when practical.
- Check Markdown links and version-control diffs. Avoid accidentally including build artifacts, IDE state, secrets, or unrelated changes.
- Explicitly mark unverified hardware mappings or upstream field names; place follow-up work in `CHANGELOG.md`.
- Report what changed, what was validated, and what remains unverified. Keep the report concise.

## Reference Routing

- [documentation-system.md](references/documentation-system.md) — document roles, structure, writing style, and deduplication rules
- [embedded-interfaces.md](references/embedded-interfaces.md) — STM32/CubeMX, CAN/DBC, hardware interfaces, timing, interrupts, and configuration details
- [project-adaptation.md](references/project-adaptation.md) — non-firmware projects, project maturity, minimum document sets, and handling exceptions

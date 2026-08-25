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
3. Classify the project and its maturity. Read [project-adaptation.md](references/project-adaptation.md) for non-typical or constrained projects, [documentation-system.md](references/documentation-system.md) before reorganizing documents, and [embedded-interfaces.md](references/embedded-interfaces.md) for MCU, CAN, hardware, generated code, or real-time behavior.
4. Build a short inventory of public interfaces, frequently changed settings, major modules, failure behavior, build paths, and known unverified assumptions.
5. Compare documentation against implementation. Correct stale claims, ambiguous units, missing ranges, wrong byte order, copied project facts, and duplicated specifications.
6. Add or reorganize only the documents the project needs. Read [documentation-system.md](references/documentation-system.md) first.
7. Validate links, examples, schemas, builds, and tests in proportion to the change. Record user-visible or maintenance-relevant changes in `CHANGELOG.md`.

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
- Maintain `CHANGELOG.md`. Record completed outcomes and remaining work without duplicating every commit or project state.
- External interfaces, frequently changed configuration, and nontrivial modules all require documentation. See [documentation-system.md](references/documentation-system.md) for detailed requirements.
- Write documentation and examples in the repository's language. Do not add unrelated-language examples.
- Distinguish verified behavior, design intent, examples, and pending decisions. Never present an assumption as implemented or verified fact.
- Be direct and readable. Avoid slogans, lectures, unnecessary jargon, filler, and repetition.

## Interface Rules

Public interfaces must be documented as contracts. Keep documentation, code, and machine-readable definitions consistent. Detailed requirements are in [documentation-system.md](references/documentation-system.md) §5 and [embedded-interfaces.md](references/embedded-interfaces.md) §3–§4.

## Shared Interface Repository

`BITFSAE/vehicle-interfaces` is the single source for team-wide CAN DBC and telemetry definitions. Changes that affect externally consumed interfaces require review there before downstream projects adapt; internal refactors and project-only configuration do not.

Boundaries and the update procedure are specified in [embedded-interfaces.md](references/embedded-interfaces.md) §3.

If a cross-repository update is not authorized or facts remain unverified, report the required change rather than claiming synchronization. Keep secrets out of public repositories.

## Review Rules

- Trace important numbers and claims back to code, generator configuration, hardware files, or approved interface definitions.
- Verify examples with actual calculations or compilation when practical.
- Explicitly mark unverified hardware mappings or upstream field names; place follow-up work in `CHANGELOG.md`.
- Report what changed, what was validated, and what remains unverified. Keep the report concise.

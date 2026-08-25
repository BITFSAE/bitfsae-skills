# Project Adaptation

## Contents

1. Choose the project profile
2. Minimum document sets
3. Adapt without weakening standards
4. Handle uncertainty and legacy projects

## 1. Choose the Project Profile

Classify by what maintainers must operate and what consumers depend on:

- embedded firmware or hardware controller;
- reusable library or driver;
- command-line or engineering tool;
- service, desktop, web, or mobile application;
- data pipeline, model, or analysis project;
- experiment or short-lived prototype;
- monorepo containing several of the above.

Use only the relevant standards. A non-CAN tool does not need a CAN document; a public library still needs an exact API contract and change history.

## 2. Minimum Document Sets

### Embedded firmware

- `README.md`
- `AGENTS.md` and `CLAUDE.md` when used by team tooling
- `CHANGELOG.md`
- build/flash document
- hardware mapping document
- external interface document plus DBC/schema when applicable
- common configuration document
- focused module documents for control, state, safety, or calibration logic

### Reusable library or driver

- README with supported environments and minimal example
- public API and error/ownership/lifetime contract
- configuration or porting guide when applicable
- changelog and compatibility notes
- tests or example consumers

### CLI, application, or service

- README with purpose, setup, run, and test path
- CLI/API/file-format contract
- configuration and environment-variable reference
- architecture/module docs only for non-obvious boundaries
- changelog, migration notes, and deployment/operations guide when applicable

### Prototype

Keep documents small but truthful: purpose, how to reproduce, inputs/outputs, known limits, and next decisions. Do not manufacture production-style documents with no useful project-specific information.

### Monorepo

Use a root README and shared rules for navigation and common workflows. Give independently built or deployed components their own README, interface/configuration documents, and changelog ownership. Avoid duplicating root policy in every subproject.

## 3. Adapt Without Weakening Standards

Allow project-specific file names and layouts when they are already clear. Evaluate the function of a document rather than mechanically enforcing a name, except for tooling-required files such as `AGENTS.md`.

Scale detail with risk, public surface, lifetime, team size, and rate of change. Safety-related firmware needs exact failure behavior; a one-off converter may need only a precise CLI and file-format description.

Retain established terminology when it is clear to the team. Define specialized terms, but do not replace useful domain language with vague generic wording.

## 4. Handle Uncertainty and Legacy Projects

- Inspect history before deleting apparently old details; they may document compatibility or hardware constraints.
- Separate current behavior from historical behavior and planned changes.
- If code and documents disagree, test or trace the implementation before rewriting both.
- Mark unverified electrical facts, upstream field mappings, calibration, and deployment assumptions.
- Improve legacy documentation incrementally when a full rewrite would create unreviewable changes.
- Preserve user changes and unrelated work in a non-clean worktree.
- Ask for direction only when an unresolved choice would materially change behavior, compatibility, safety, or document ownership.

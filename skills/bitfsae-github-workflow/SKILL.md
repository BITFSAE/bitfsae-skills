---
name: bitfsae-github-workflow
description: "Apply BITFSAE Git/GitHub rules in BITFSAE repositories: feature branches and PR review, protected main, shared CAN/telemetry interface sync, and credential or build-artifact checks. Trigger when preparing commits, pushes, PRs, reviews, or merges, when asked whether a change can be pushed directly, merged, or requires vehicle-interfaces, or when handling secrets or generated files. Do not trigger for generic Git help, non-BITFSAE repositories, or ordinary code changes."
---

# BITFSAE GitHub Workflow

## Goal

Keep BITFSAE changes reviewable, traceable, and free of credentials or generated artifacts, while respecting each repository's existing rules and the maintainer's choices.

## Team Constraints

- Work on a feature branch based on a current main. Do not push directly to main or rewrite published history.
- Follow the repository's existing branch and commit conventions. When it has none, use a clear prefix such as feat/, fix/, or docs/ and a concise type(scope): subject message.
- Internal collaboration uses a branch and pull request rather than forks, unless the project explicitly uses a fork workflow.
- Use the repository's pull request template when present. State what changed, why, how it was verified, and what remains unverified. Never claim an untested result passed.
- Request review from the relevant owner, address requested changes, and merge only after approval.
- When a change alters an externally consumed CAN or telemetry definition, first update and review BITFSAE/vehicle-interfaces, then adapt the consuming projects. Internal refactors, compliance-restoring fixes, and project-only configuration do not require this.
- Never commit credentials, secrets, or generated artifacts. Follow the repository .gitignore and do not force-add ignored files.
- Treat repository-specific instructions and existing conventions as authoritative.

## Checks

- Confirm the base is a current main and the work is on a feature branch.
- Confirm whether the change affects an externally consumed CAN or telemetry definition.
- Confirm the diff contains no credentials, generated products, ignored files, or unrelated edits.
- Confirm verification evidence reflects what was actually run.
- Confirm the reviewer is the relevant owner and the merge mode follows that repository's choice.

When a constraint is missing or cannot be verified, do not claim compliance. Report the specific gap and the required action instead.

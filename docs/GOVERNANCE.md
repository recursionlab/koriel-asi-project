<!-- docs/GOVERNANCE.md -->
Project governance and rules for Koriel-ASI.

Scope
- This document defines high-level governance for repository stewardship, CI enforcement, release process, and review rules.

Principles
- Minimal, auditable changes. Prefer small, test-covered commits.
- Automated enforcement: CI must pass before merge to `main`.
- Conservative maintenance: prefer non-behavioral edits for hygiene unless clearly required by tests.

Roles
- Owners: repository administrators with branch protection rights.
- Maintainers: trusted contributors who can approve PRs and merge after CI and approvals.
- Contributors: anyone who opens issues or PRs.

Branching and merging
- `main` is the canonical branch and must be protected by branch rules.
- Feature work occurs on short-lived branches named `feat/*`, `fix/*`, or `copilot/*`.
- Merge policy: PRs must have
  - passing CI (lint, type, tests)
  - at least one reviewer approval from Maintainers (two approvals for changes touching core modules)
  - a descriptive changelog entry when behavior is changed

CI and enforcement
- CI runs: ruff (lint), pytest (tests), optional mypy (typecheck) when configured.
- No PR should be merged if any CI check fails. Use `--force-with-lease` only with explicit owner approval.

Releases
- Keep a `CHANGELOG.md` with Unreleased section. Tag releases semantically (vMAJOR.MINOR.PATCH).

Security and disclosures
- Report security issues privately via the repository's security policy or the repository owner.

Governance changes
- Governance changes require approval from two Owners and a short transition plan.

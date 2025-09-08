<!-- docs/branch-protection.md -->
# Branch protection recommendations

Admins should apply the following settings for the `main` branch via repository settings:

- Require status checks to pass before merging:
  - `CI - Lint & Test` (ruff + pytest)
  - `typecheck` (mypy) — optional but recommended
- Require pull request reviews before merging:
  - At least 1 approval for regular PRs
  - Require 2 approvals for changes under `src/` or core modules
- Restrict who can push to `main`:
  - Allow Owners only for emergency force-pushes; otherwise block force pushes
- Require linear history (no merge commits) and enable signed commits if feasible.

These settings provide a guarded, auditable process and enforce the CI you configured.

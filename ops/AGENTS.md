# Agent Collaboration Guide

This repo supports multiple autonomous AI contributors. Use these conventions:

- Branch prefixes: `copilot/`, `codex/`, `probe/`, `adopt/`, `ops/`.
- Labels:
  - `agent` — PRs authored by agents
  - `perm-probe` — permission probes; automerge on green
  - `automerge` — merge automatically once CI is green
  - `docs`, `python`, `ops` — scope labels
- Commands (comment on a PR):
  - `/sitrep` — generate branch/PR sitrep and upload as artifact
  - `/label <name>` — add a label
  - `/automerge` — request auto-merge on green
  - `/adopt` — create an adoption branch for integration

Workflows:
- PR Intake Triage: labels agent PRs and posts checklist.
- PR Commands: responds to `/sitrep`, `/label`, `/automerge`, `/adopt`.
- Auto-merge on Label: merges PR when `automerge` and checks are green.
- Nightly Sitrep: uploads a repo-wide sitrep.
- Auto branch cleanup: deletes head branch after merge.

Make targets (local):
- `make sitrep` — write `artifacts/ci_smoke/git_sitrep.md`
- `make prune-merged` — list stale remote branches (dry run)
- `make prune-merged-exec` — delete stale remote branches
- `make pr-conflicts` — report conflicts for DIRTY PRs
- `make pr-conflicts-fix` — attempt clean merges of main

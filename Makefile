.PHONY: bundle setup test benchmark sitrep git-sitrep prune-merged prune-merged-exec pr-conflicts pr-conflicts-fix agent-ops

bundle:
	python scripts/bundle.py

setup:
	bash scripts/setup.sh

test:
	bash scripts/run_tests.sh

benchmark:
	bash scripts/run_ab.sh

# Generate Git/PR status report under artifacts/ci_smoke/git_sitrep.md
git-sitrep:
	python3 scripts/git_sitrep.py

# Alias for sitrep
sitrep: git-sitrep
	@echo "Wrote artifacts/ci_smoke/git_sitrep.md"

# List remote branches safe to prune (merged PRs) - dry run
prune-merged:
	python3 scripts/git_prune_merged.py

# Actually delete those remote branches
prune-merged-exec:
	python3 scripts/git_prune_merged.py --execute

# Generate a merge-conflict report for DIRTY PRs (default) or specific PRs: make pr-conflicts PRS="7 14"
pr-conflicts:
	python3 scripts/pr_conflict_report.py $(if $(PRS),$(PRS),)

# Attempt to push a clean merge of main into PR branches (safe; only if clean)
pr-conflicts-fix:
	python3 scripts/pr_conflict_report.py --update-clean $(if $(PRS),$(PRS),)

# Label agent PRs, post guidance, and trigger sitrep on a subset
agent-ops:
	python3 scripts/agent_ops.py

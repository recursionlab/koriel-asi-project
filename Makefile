.PHONY: bundle setup test benchmark sitrep git-sitrep prune-merged prune-merged-exec pr-conflicts pr-conflicts-fix agent-ops tidy-root tidy-assert lint fmt pre-commit

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

# Inventory root and propose tidy moves (use APPLY=1 to apply)
tidy-root:
	python3 scripts/inventory_root.py $(if $(APPLY),--apply,)

# Assert root cleanliness (non-zero if messy)
tidy-assert:
	python3 scripts/inventory_root.py --assert-clean

lint:
	pre-commit run flake8 --all-files || true

fmt:
	pre-commit run black --all-files || true
	pre-commit run isort --all-files || true

pre-commit:
	pre-commit run --all-files || true

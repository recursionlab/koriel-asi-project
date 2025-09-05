.PHONY: bundle setup test benchmark sitrep git-sitrep prune-merged prune-merged-exec

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

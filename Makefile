.PHONY: bundle setup test benchmark lint clean install dev-install run-dry experiment-dry doctor seed-grid-smoke operator-gate perf-canary apply-updates automation-smoke

# Development setup
setup:
	bash scripts/setup.sh

install:
	pip install -e .

dev-install:
	pip install -e .
	pip install pytest ruff

# Code quality
lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff format src/ tests/

# Testing
test:
	pytest tests/ -v -m "not slow"

test-all:
	pytest tests/ -v

test-slow:
	pytest tests/ -v -m "slow"

# Running
run-dry:
	python koriel-run run --dry-run

run-quick:
	python koriel-run run --config configs/quick_test.yaml

# Experiments (with safety)
experiment-dry:
	python koriel-run experiment --name brutal_consciousness_validation --allow-experiments --dry-run

experiment-list:
	find experiments/ -name "*.py" -exec basename {} .py \;

# Maintenance
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache build/ dist/ *.egg-info/

bundle:
	python scripts/bundle.py

benchmark:
	bash scripts/run_ab.sh

# Doctor command - sanity check for dependencies and environment
doctor:
	@python -c "import sys, importlib as I; mods=['pytest','hypothesis','sympy','ruff','mypy']; missing=[m for m in mods if not I.util.find_spec(m.split('[',1)[0])]; print('python',sys.version.split()[0]); print('ok' if not missing else f'missing:{missing}')"

# Seed grid smoke test - Item 2
seed-grid-smoke:
	python scripts/seed_grid_smoke.py

# Operator validator gate - Item 7
operator-gate:
	python scripts/validate_operators.py
	@python -c "import json; d=json.load(open('artifacts/ci_smoke/operator_mapping.json')); assert d.get('refs_ok') and not d.get('errors'), d; print('operator-gate ok')"

# Performance canary - Item 9 (optional, controlled by env)
perf-canary:
	python scripts/bench.py --out artifacts/ci_smoke/bench --items $${PERF_ITEMS:-50}
	@python -c "import json,os; th=json.load(open('artifacts/ci_smoke/bench/results.json')).get('throughput_items_per_s',0); min_thr=float(os.environ.get('PERF_MIN_THR','5')); assert th >= min_thr, f'Throughput {th} < {min_thr}'; print(f'perf-canary ok: {th:.1f} items/s')"

# Update applicator - Item 10
apply-updates:
	python scripts/apply_manifesto_updates.py

# Comprehensive automation smoke test - run all 80/20 features
automation-smoke:
	@echo "Running 80/20 automation pack..."
	make doctor
	make seed-grid-smoke
	make operator-gate
	@echo "Automation smoke test completed successfully!"

.PHONY: bundle setup test benchmark lint clean install dev-install run-dry experiment-dry sitrep apply-updates validate-updates chat-smoke

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

sitrep:
	python scripts/sitrep.py

chat-smoke:
	mkdir -p artifacts/ci_smoke
	echo "Running smoke chat test"
	echo "x**2 - 1" > artifacts/ci_smoke/chat.log
	echo '{"math_available": true, "sympy_version": "1.12"}' >> artifacts/ci_smoke/chat.log

.PHONY: apply-updates validate-updates
apply-updates:
	python scripts/apply_manifesto_updates.py

validate-updates:
	python -m scripts.validate_operators
	-pytest -q --tb=no
	python scripts/sitrep.py

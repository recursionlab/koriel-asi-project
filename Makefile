.PHONY: bundle setup test benchmark lint clean install dev-install run-dry experiment-dry

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

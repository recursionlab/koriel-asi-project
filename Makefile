.PHONY: bundle setup test benchmark lint clean install dev-install run-dry experiment-dry doctor fix

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

# Developer speed targets
doctor:
	@echo "🔍 Environment Check"
	@python --version
	@echo "NumPy: $$(python -c 'import numpy; print(numpy.__version__)')"
	@echo "Environment variables:"
	@echo "  PYTHONHASHSEED: $${PYTHONHASHSEED:-not_set}"
	@echo "  OMP_NUM_THREADS: $${OMP_NUM_THREADS:-not_set}"
	@python -c "from src.determinism import assert_deterministic_environment; assert_deterministic_environment(); print('✓ Deterministic environment OK')" || echo "✗ Deterministic environment not configured"
	@python metrics_server.py --test || echo "✗ Metrics validation failed"

fix:
	ruff format src/ tests/
	ruff check src/ tests/ --fix
	@echo "✓ Code formatting and linting fixes applied"

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

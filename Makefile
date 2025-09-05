.PHONY: bundle setup test benchmark

bundle:
	python scripts/bundle.py

setup:
	bash scripts/setup.sh

test:
	bash scripts/run_tests.sh

benchmark:
	bash scripts/run_ab.sh

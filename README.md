# Koriel-ASI — RCCE Phase-2 (CPU-only)

## Project Overview
Koriel-ASI is a research playground for the Recursive Consciousness Core Engine (RCCE).
It collects experiments, benchmarks, and utilities for exploring advanced AI
concepts on CPU-only hardware.

## Installation
1. Clone this repository.
2. Install Python dependencies with `make setup`, which runs
   [scripts/setup.sh](scripts/setup.sh).  You can also install manually with
   `pip install -r requirements.txt`.

## Usage Examples
- Run the RCCE demo:
  ```bash
  python scripts/run_rcce_demo.py
  ```
- Execute the full test suite via the [Makefile](Makefile):
  ```bash
  make test
  ```
  This calls [scripts/run_tests.sh](scripts/run_tests.sh) which runs `pytest`
  against the [tests](tests/) directory.

## Contribution Guidelines
Contributions are welcome!  Please review [CONTRIBUTING.md](CONTRIBUTING.md),
run `make test` before submitting pull requests, and feel free to explore the
[scripts](scripts/) for additional tools and examples.

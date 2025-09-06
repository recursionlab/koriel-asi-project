# Koriel ASI Project

This repository explores field-theoretic approaches to artificial super intelligence and quantum reality field theory. Over time the project has accumulated many experiments, tests and research artifacts which makes navigation difficult. This document outlines a high level plan for regaining structure and keeping new contributions organized.

## Installation

Install the project along with its runtime dependencies using `pip`:

```bash
# install directly from the source tree
pip install -e .

# or generate requirements.txt and use it
python scripts/generate_requirements.py
pip install -r requirements.txt
```

## Recommended Directory Layout

- `src/` – core Python modules implementing the main algorithms.
- `tests/` – automated tests. Stand‑alone scripts like `advanced_qrft_tests.py`, `brutal_qrft_tests.py` and other `*test.py` files should move here.
- `examples/` – minimal runnable examples showing how to use the library.
- `docs/` – long form documentation, design notes and the manifesto.
- `experiments/` and `research/` – exploratory notebooks, reports and results that are not part of the main package.
- `scripts/` – helper scripts or command line entry points for demos.
- `prompts/` – prompt templates and conversation logs.

## Housekeeping Guidelines

1. Prefer snake_case for Python files and directories.
2. Keep imports relative within `src` and avoid executing heavy code at import time.
3. Consolidate duplicated logic in scripts into reusable functions under `src`.
4. Declare runtime dependencies in `pyproject.toml` and regenerate `requirements.txt` using `scripts/generate_requirements.py` when needed.
5. Add new tests alongside features and ensure `pytest` passes.

## Next Steps

1. Audit top‑level Python files and relocate them into `src/`, `tests/`, or `examples/` as appropriate.
2. Establish continuous integration to run the test suite and linting on every commit.
3. Provide a quickstart guide and module level documentation in `docs/`.

See also: `docs/REPO_STRUCTURE.md` for conventions and a helper script to preview/apply tidy moves.

These steps should make the project easier to navigate and contribute to while preserving the experimental spirit of the work.

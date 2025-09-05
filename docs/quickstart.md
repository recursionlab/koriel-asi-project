# Quick start

This guide walks through training the RCCE model and running benchmark
evaluations.

## 1. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate    # `Scripts\\activate` on Windows
pip install -r requirements.txt
```

## 2. Train the model

The [training script](../src/train.py) loads configuration from `config/rcce.yaml`
and writes metrics to `logs/`.

```bash
python src/train.py
```

## 3. Evaluate benchmarks

Run the consciousness benchmark suite to generate a report under
`rcce-minimal/outputs/`.

```bash
python rcce-minimal/src/benchmarks.py
```

The script prints a summary and saves `consciousness_benchmark_report.json`.

## 4. Run tests

```bash
python -m pytest
```

For Windows users, equivalent PowerShell scripts are in the `scripts/` directory:
`setup.ps1` and `run_tests.ps1`.


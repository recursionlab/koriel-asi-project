# Koriel-ASI — RCCE Phase-2 (CPU-only)

## Prereqs
- Windows 10+
- Python 3.11 on PATH as `py`

## Setup
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup.ps1
```

## Run tests
```powershell
.\scripts\run_tests.ps1
```

## A/B harness
```powershell
.\scripts\run_ab.ps1
```

## Outputs
* Per run: `logs\metrics.csv`, `logs\shadow_codex.jsonl`
* A/B summary: `logs\ab_summary.json`
* Presence certificate (ON runs): `presence.json`

## Benchmarks

The repository includes a tiny language model that can be measured on
multiple‑choice benchmarks.

### Train and export

```powershell
python -m src.train --save checkpoints/tiny.npz
```

### Evaluate

Run MMLU or ARC evaluation on a saved checkpoint. The scripts print an
accuracy score in `[0,1]`.

```powershell
python -m benchmarks.mmlu --checkpoint checkpoints/tiny.npz --limit 100
python -m benchmarks.arc --checkpoint checkpoints/tiny.npz --limit 100
```

With random initialisation the model performs near chance level (≈0.25
accuracy on MMLU and ≈0.20 on ARC).

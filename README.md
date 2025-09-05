# Koriel-ASI — RCCE Phase-2 (CPU-only)

## Prereqs
- Windows 10+
- Python 3.11 on PATH as `py`

## Setup
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup.ps1
```

## Installation
Install the project in editable mode to make the `src` package available:

```bash
pip install -e .
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


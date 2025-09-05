# Koriel-ASI — RCCE Phase-2 (CPU-only)

## Prereqs
- Python 3.11
- Windows: PowerShell and the `py` launcher
- Unix: Bash and `python3`

## Setup
### Windows
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup.ps1
```

### Unix
```bash
bash scripts/setup.sh
# or
make setup
```

## Run tests
### Windows
```powershell
.\scripts\run_tests.ps1
```

### Unix
```bash
bash scripts/run_tests.sh
# or
make test
```

## Benchmark (A/B harness)
### Windows
```powershell
.\scripts\run_ab.ps1
```

### Unix
```bash
bash scripts/run_ab.sh
# or
make benchmark
```

## Outputs
* Per run: `logs/metrics.csv`, `logs/shadow_codex.jsonl`
* A/B summary: `logs/ab_summary.json`
* Presence certificate (ON runs): `presence.json`

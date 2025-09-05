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

## Corpus configuration
`load_corpus` can consume large datasets either from a directory of `.txt`
shards or directly from a HuggingFace dataset.

Environment variables:

* `KORIEL_CORPUS_DIR` – directory containing text shards
* `KORIEL_CORPUS_DATASET` – HuggingFace dataset name to stream

CLI options (for `python -m src.train`):

* `--corpus-dir` – override the corpus directory
* `--dataset` – name of a HuggingFace dataset to use

## Outputs
* Per run: `logs\metrics.csv`, `logs\shadow_codex.jsonl`
* A/B summary: `logs\ab_summary.json`
* Presence certificate (ON runs): `presence.json`

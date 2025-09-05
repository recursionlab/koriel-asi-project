# scripts/run_tests.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$proj = Split-Path $root
Set-Location $proj
$env:PYTHONPATH = "$proj"
$py = ".\.venv\Scripts\python.exe"
& $py -m pytest tests
if ($LASTEXITCODE -ne 0) { exit 1 } else { exit 0 }

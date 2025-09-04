# scripts/run_ab.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$proj = Split-Path $root
Set-Location $proj
$env:PYTHONPATH = "$proj"
$py = ".\.venv\Scripts\python.exe"
& $py .\src\ab.py
if ($LASTEXITCODE -ne 0) { exit 1 } else { exit 0 }

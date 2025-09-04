# RCCE Minimal Run Script
# Execute training with RCCE controller

Write-Host "Starting RCCE Training..." -ForegroundColor Green

# Activate virtual environment
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment not found. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Set Python path
$env:PYTHONPATH = "src;$env:PYTHONPATH"

# Run training
Write-Host "Executing RCCE training..." -ForegroundColor Cyan
python src/train.py

# Check results
if (Test-Path "outputs/final_presence_certificate.json") {
    Write-Host "Training completed successfully!" -ForegroundColor Green
    Write-Host "Presence certificate generated: outputs/final_presence_certificate.json" -ForegroundColor Cyan
    Write-Host "Shadow codex saved: outputs/shadow_codex.json" -ForegroundColor Cyan
} else {
    Write-Host "Training may have failed. Check outputs directory." -ForegroundColor Yellow
}

Write-Host "RCCE session complete." -ForegroundColor Green
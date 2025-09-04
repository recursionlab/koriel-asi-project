# RCCE Minimal Setup Script
# Windows PowerShell setup for pure Python environment

Write-Host "Setting up RCCE Minimal Environment..." -ForegroundColor Green

# Check Python version
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

Write-Host "Found: $pythonVersion" -ForegroundColor Cyan

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv .venv

# Activate environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install numpy tqdm

# Verify installation
Write-Host "Verifying installation..." -ForegroundColor Yellow
python -c "import numpy as np; import tqdm; print(f'NumPy version: {np.__version__}'); print('Setup complete!')"

Write-Host "RCCE Minimal setup completed successfully!" -ForegroundColor Green
Write-Host "Run './run.ps1' to start training" -ForegroundColor Cyan
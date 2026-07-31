<#
.SYNOPSIS
Sets up the SpidyGlass AI Backend environment on Windows 11.
#>

$ErrorActionPreference = "Stop"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "         SpidyGlass AI - Environment Setup          " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# 1. Detect Python
$pythonCmd = "python"
try {
    $pyVersion = & python --version 2>&1
} catch {
    try {
        $pyVersion = & py --version 2>&1
        $pythonCmd = "py"
    } catch {
        Write-Host "ERROR: Python is not installed or not in PATH." -ForegroundColor Red
        Write-Host ""
        Write-Host "SETUP GUIDE:" -ForegroundColor Yellow
        Write-Host "1. Download Python 3.12 from https://www.python.org/downloads/windows/"
        Write-Host "2. Run the installer."
        Write-Host "3. CRITICAL: Check the box 'Add Python 3.x to PATH' at the bottom of the installer window."
        Write-Host "4. Complete the installation and restart your terminal before running this script again."
        exit 1
    }
}

Write-Host "[OK] Found Python: $pyVersion" -ForegroundColor Green

# 2. Check Docker (Optional but recommended for DB/Redis)
$dockerAvailable = $false
try {
    $dockerVersion = & docker --version 2>&1
    $dockerAvailable = $true
    Write-Host "[OK] Found Docker: $dockerVersion" -ForegroundColor Green
    
    Write-Host "Starting PostgreSQL and Redis containers..." -ForegroundColor Cyan
    docker-compose up -d db redis
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARNING] docker-compose failed to start DB/Redis. Please check Docker Desktop." -ForegroundColor Yellow
    } else {
        Write-Host "[OK] Infrastructure containers started." -ForegroundColor Green
    }
} catch {
    Write-Host "[WARNING] Docker not found. You will need a local PostgreSQL and Redis instance running manually." -ForegroundColor Yellow
}

# 3. Virtual Environment
$backendDir = Join-Path -Path $PWD -ChildPath "backend"
$venvDir = Join-Path -Path $backendDir -ChildPath ".venv"

if (-not (Test-Path -Path $venvDir)) {
    Write-Host "Creating virtual environment in backend/.venv..." -ForegroundColor Cyan
    & $pythonCmd -m venv $venvDir
} else {
    Write-Host "[OK] Virtual environment already exists." -ForegroundColor Green
}

# Activate VENV for the script
$activateScript = Join-Path -Path $venvDir -ChildPath "Scripts\Activate.ps1"
if (Test-Path -Path $activateScript) {
    . $activateScript
} else {
    Write-Host "ERROR: Could not find activation script at $activateScript" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Virtual environment activated." -ForegroundColor Green

# 4. Install dependencies
Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip | Out-Null

$requirementsFile = Join-Path -Path $backendDir -ChildPath "requirements.txt"
if (Test-Path -Path $requirementsFile) {
    Write-Host "Installing dependencies from requirements.txt (this may take a few minutes)..." -ForegroundColor Cyan
    python -m pip install -r $requirementsFile
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Dependency installation failed." -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Dependencies installed successfully." -ForegroundColor Green
} else {
    Write-Host "ERROR: backend/requirements.txt not found!" -ForegroundColor Red
    exit 1
}

# 5. Alembic Migrations (Optional, wrap in try/catch if alembic.ini doesn't exist yet)
Set-Location -Path $backendDir
if (Test-Path -Path "alembic.ini") {
    Write-Host "Running Database Migrations..." -ForegroundColor Cyan
    alembic upgrade head
    Write-Host "[OK] Migrations applied." -ForegroundColor Green
} else {
    Write-Host "[INFO] alembic.ini not found, skipping migrations." -ForegroundColor Yellow
}

# 6. Verify Environment
Write-Host "Verifying Environment..." -ForegroundColor Cyan
python ../verify_environment.py

# 7. Start FastAPI
Write-Host "[*] Starting Backend Server on port 8000..." -ForegroundColor Cyan
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

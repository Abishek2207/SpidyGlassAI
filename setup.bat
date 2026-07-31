@echo off
setlocal EnableDelayedExpansion

echo ====================================================
echo          SpidyGlass AI - Environment Setup          
echo ====================================================

:: 1. Detect Python
set PYTHON_CMD=python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    py --version >nul 2>&1
    if !ERRORLEVEL! neq 0 (
        echo ERROR: Python is not installed or not in PATH.
        echo.
        echo SETUP GUIDE:
        echo 1. Download Python 3.12 from https://www.python.org/downloads/windows/
        echo 2. Run the installer.
        echo 3. CRITICAL: Check the box 'Add Python 3.x to PATH' at the bottom of the installer window.
        echo 4. Complete the installation and restart your terminal before running this script again.
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
)

echo [OK] Found Python.

:: 2. Check Docker
docker --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] Found Docker. Starting PostgreSQL and Redis containers...
    docker-compose up -d db redis
    if !ERRORLEVEL! neq 0 (
        echo [WARNING] docker-compose failed to start DB/Redis. Please check Docker Desktop.
    ) else (
        echo [OK] Infrastructure containers started.
    )
) else (
    echo [WARNING] Docker not found. You will need a local PostgreSQL and Redis instance running manually.
)

:: 3. Virtual Environment
cd backend
if not exist ".venv" (
    echo Creating virtual environment in backend\.venv...
    %PYTHON_CMD% -m venv .venv
) else (
    echo [OK] Virtual environment already exists.
)

if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Could not find activation script.
    exit /b 1
)

call .venv\Scripts\activate.bat
echo [OK] Virtual environment activated.

:: 4. Install dependencies
echo Upgrading pip...
python -m pip install --upgrade pip >nul

if exist "requirements.txt" (
    echo Installing dependencies from requirements.txt (this may take a few minutes)...
    python -m pip install -r requirements.txt
    if !ERRORLEVEL! neq 0 (
        echo ERROR: Dependency installation failed.
        exit /b 1
    )
    echo [OK] Dependencies installed successfully.
) else (
    echo ERROR: backend\requirements.txt not found!
    exit /b 1
)

:: 5. Alembic Migrations
if exist "alembic.ini" (
    echo Running Database Migrations...
    alembic upgrade head
    echo [OK] Migrations applied.
) else (
    echo [INFO] alembic.ini not found, skipping migrations.
)

:: 6. Verify Environment
echo Verifying Environment...
python ..\verify_environment.py

:: 7. Start FastAPI
echo [*] Starting Backend Server...
start /b cmd /c "cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

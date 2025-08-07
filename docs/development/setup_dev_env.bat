@echo off
REM Virtual Environment Setup Script for FreeCAD AI Addon (Windows)
REM This script sets up a development environment for the FreeCAD AI Addon

setlocal enabledelayedexpansion

echo === FreeCAD AI Addon Development Setup (Windows) ===
echo.

REM Check if Python is available
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8 or later and add it to PATH.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python %PYTHON_VERSION% found

REM Check Python version (basic check for 3.x)
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.8+ is required
    pause
    exit /b 1
)
echo [SUCCESS] Python version is compatible

REM Create virtual environment
echo [INFO] Creating virtual environment...
if exist venv (
    echo [WARNING] Virtual environment already exists.
    set /p response="Remove it? (y/N): "
    if /i "!response!"=="y" (
        rmdir /s /q venv
        echo [INFO] Removed existing virtual environment
    ) else (
        echo [INFO] Using existing virtual environment
        goto activate_venv
    )
)

python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment created

:activate_venv
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
echo [SUCCESS] Virtual environment activated

REM Install dependencies
echo [INFO] Installing dependencies...
python -m pip install --upgrade pip

if exist requirements.txt (
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install requirements
        pause
        exit /b 1
    )
    echo [SUCCESS] Requirements installed
) else (
    echo [ERROR] requirements.txt not found
    pause
    exit /b 1
)

REM Install development dependencies
pip install pytest pytest-cov black flake8 mypy sphinx sphinx-rtd-theme
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install development dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Development dependencies installed

REM Setup pre-commit hooks
echo [INFO] Setting up pre-commit hooks...
pip install pre-commit

if not exist .pre-commit-config.yaml (
    echo repos: > .pre-commit-config.yaml
    echo   - repo: https://github.com/psf/black >> .pre-commit-config.yaml
    echo     rev: 23.9.1 >> .pre-commit-config.yaml
    echo     hooks: >> .pre-commit-config.yaml
    echo       - id: black >> .pre-commit-config.yaml
    echo         language_version: python3 >> .pre-commit-config.yaml
    echo   - repo: https://github.com/pycqa/flake8 >> .pre-commit-config.yaml
    echo     rev: 6.1.0 >> .pre-commit-config.yaml
    echo     hooks: >> .pre-commit-config.yaml
    echo       - id: flake8 >> .pre-commit-config.yaml
    echo   - repo: https://github.com/pre-commit/mirrors-mypy >> .pre-commit-config.yaml
    echo     rev: v1.5.1 >> .pre-commit-config.yaml
    echo     hooks: >> .pre-commit-config.yaml
    echo       - id: mypy >> .pre-commit-config.yaml
    echo         additional_dependencies: [types-requests] >> .pre-commit-config.yaml
    echo [SUCCESS] Created pre-commit configuration
)

pre-commit install
echo [SUCCESS] Pre-commit hooks installed

REM Create development scripts
echo [INFO] Creating development scripts...

REM Test script
echo @echo off > run_tests.bat
echo call venv\Scripts\activate.bat >> run_tests.bat
echo python -m pytest tests/ -v --cov=freecad_ai_addon --cov-report=html >> run_tests.bat

REM Lint script
echo @echo off > run_lint.bat
echo call venv\Scripts\activate.bat >> run_lint.bat
echo echo Running Black... >> run_lint.bat
echo black freecad_ai_addon/ >> run_lint.bat
echo echo Running Flake8... >> run_lint.bat
echo flake8 freecad_ai_addon/ >> run_lint.bat
echo echo Running MyPy... >> run_lint.bat
echo mypy freecad_ai_addon/ --ignore-missing-imports >> run_lint.bat

REM Format script
echo @echo off > format_code.bat
echo call venv\Scripts\activate.bat >> format_code.bat
echo black freecad_ai_addon/ >> format_code.bat
echo black tests/ >> format_code.bat

echo [SUCCESS] Development scripts created

echo.
echo [SUCCESS] Development environment setup complete!
echo.
echo To get started:
echo   1. Activate the virtual environment: venv\Scripts\activate.bat
echo   2. Run tests: run_tests.bat
echo   3. Format code: format_code.bat
echo   4. Run linting: run_lint.bat
echo.
echo The virtual environment includes:
echo   • All required dependencies from requirements.txt
echo   • Development tools (pytest, black, flake8, mypy)
echo   • Documentation tools (sphinx)
echo   • Pre-commit hooks for code quality
echo.
pause

@echo off
REM Quick Setup Script for Tableau Knowledge MCP
REM Run this anytime you need to set up or reset your environment

echo ========================================
echo Tableau Knowledge MCP - Quick Setup
echo ========================================
echo.

REM Check if venv exists
if exist venv (
    echo [1/3] Virtual environment already exists
) else (
    echo [1/3] Creating virtual environment...
    py -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Try running: py -m venv venv
        pause
        exit /b 1
    )
    echo      Virtual environment created successfully!
)

echo.
echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo [3/3] Installing/updating dependencies...
py -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Virtual environment is now activated.
echo You can now run:
echo   - python scripts\index_books.py --pdf-dir "path\to\pdfs"
echo   - python src\server.py
echo   - pytest tests/
echo.
echo To deactivate later, type: deactivate
echo.
pause

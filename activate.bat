@echo off
REM Quick activation script - use this to start working
REM Just double-click this file or run: activate

echo Activating Tableau Knowledge MCP environment...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo.
    echo ERROR: Virtual environment not found!
    echo Run setup.bat first to create the environment.
    pause
    exit /b 1
)

echo.
echo Environment activated! (venv)
echo.
echo Quick commands:
echo   Index PDFs:    python scripts\index_books.py --pdf-dir "path"
echo   Test server:   python src\server.py
echo   Run tests:     pytest tests/
echo   Deactivate:    deactivate
echo.

REM Keep the window open in activated state
cmd /k

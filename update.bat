@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    pause
    exit /b 1
)

REM Prefer .venv
set "VENV_DIR=.venv"

if not exist "%VENV_DIR%" (
    echo Creating virtual environment in %VENV_DIR% ...
    python -m venv "%VENV_DIR%"
)

call "%VENV_DIR%\Scripts\activate.bat"

python -m pip install --upgrade pip

if exist requirements.txt (
    echo Installing dependencies from requirements.txt ...
    pip install -r requirements.txt
) else (
    echo requirements.txt not found. Installing Django only ...
    pip install Django
)

echo Done.
pause
endlocal

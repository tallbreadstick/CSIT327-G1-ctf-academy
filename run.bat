@echo off
setlocal
cd /d "%~dp0"

REM Prefer .venv, fallback to venv
set "VENV_DIR=.venv"
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    if exist "venv\Scripts\activate.bat" (
        set "VENV_DIR=venv"
    )
)

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo No virtual environment found. Run deps.bat first to create and install dependencies.
    goto :end
)

call "%VENV_DIR%\Scripts\activate.bat"

REM Pass through any args to manage.py (e.g., run.bat 0.0.0.0:8000)
python ctf_academy\manage.py runserver 0.0.0.0:8000

:end
pause
endlocal

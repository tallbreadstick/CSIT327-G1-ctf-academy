@echo off
setlocal
cd /d "%~dp0"

REM Go to Tailwind source directory
cd ctf_academy\theme\static_src

REM Check if Node.js is installed
where npm >nul 2>nul
if errorlevel 1 (
    echo Node.js and npm are not installed or not in PATH.
    pause
    exit /b 1
)

echo Installing Node.js dependencies ...
npm install

echo Building TailwindCSS assets ...
npm run build

echo Building Django tailwind
cd ..\..
python manage.py tailwind build

echo Tailwind build complete.
pause
endlocal

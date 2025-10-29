@echo off
setlocal
cd /d "%~dp0"

echo === Step 1: Updating Python environment ===
call update.bat

echo.
echo === Step 2: Building Tailwind assets ===
call tailwind.bat

echo.
echo === Step 3: Starting Django development server ===
call run.bat

endlocal

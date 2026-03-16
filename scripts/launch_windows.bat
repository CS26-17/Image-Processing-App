@echo off
setlocal

REM This script lives in scripts\ but the project root is one level up
cd /d "%~dp0.."

echo Project root: %CD%

REM Create virtual env if it doesn't exist
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  python -m venv .venv
)

REM Install / upgrade dependencies
echo Installing dependencies...
call ".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
call ".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet

REM Launch the app
echo Launching app...
call ".venv\Scripts\python.exe" image_processing_app.py

endlocal
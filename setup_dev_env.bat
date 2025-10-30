@echo off
REM Simple Setup Script - Windows

echo Setting up development environment...

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install requirements
pip install -r requirements.txt

echo.
echo Setup complete
echo.
echo To start developing:
echo   1. Activate environment: venv\Scripts\activate
echo   2. Run app: python image_difference_app.py
echo   3. Open in VS Code: code .
echo.
pause

@echo off
REM Quick Fix Script for PyQt6 DLL Error on Windows

echo ========================================
echo PyQt6 DLL Error - Quick Fix
echo ========================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    if exist venv\Scripts\activate.bat (
        call venv\Scripts\activate.bat
    ) else (
        echo ERROR: Virtual environment not found!
        echo Please run this from your project directory.
        pause
        exit /b 1
    )
)

echo Current Python version:
python --version
echo.

echo Step 1: Uninstalling PyQt6...
pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip
echo.

echo Step 2: Clearing pip cache...
pip cache purge
echo.

echo Step 3: Installing stable PyQt6 version...
pip install PyQt6==6.4.0
echo.

echo Step 4: Testing PyQt6...
python -c "from PyQt6.QtWidgets import QApplication; print('✓ PyQt6 is working!')"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo ✓ SUCCESS! PyQt6 is now working.
    echo ========================================
    echo.
    echo You can now run your application.
) else (
    echo.
    echo ========================================
    echo ✗ PyQt6 still not working.
    echo ========================================
    echo.
    echo Please try these steps:
    echo 1. Install Visual C++ Redistributables:
    echo    - Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo    - Install and restart computer
    echo.
    echo 2. Or use PySide6 instead:
    echo    pip uninstall PyQt6
    echo    pip install PySide6
    echo.
    echo See PYQT6_FIX.md for more solutions.
)

echo.
pause

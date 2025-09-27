@echo off
echo Installing Aeronix Test Generator v1.0.0

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt

echo Installation complete!
echo Run: python UI.py
pause

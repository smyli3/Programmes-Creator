@echo off
echo Setting up Snowsports Program Manager...

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Create a virtual environment
echo Creating virtual environment...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
)

REM Activate the virtual environment and install packages
echo Installing required packages...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install flask pandas openpyxl

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Setup completed successfully!
    echo.
    echo To start the application, run: run_app.bat
) else (
    echo.
    echo Failed to install required packages.
)

pause

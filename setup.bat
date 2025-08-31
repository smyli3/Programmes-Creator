@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: ====================================
:: Setup Script for Snowsports Program Manager
:: ====================================

echo ############################################
echo #  Snowsports Program Manager Setup  #
echo ############################################
echo.

:: Check if Python is installed
echo [*] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2 delims= " %%a in ('python -c "import sys; print('{0}.{1}'.format(sys.version_info[0], sys.version_info[1]))"') do set PYTHON_VERSION=%%a
if !PYTHON_VERSION! LSS 3.8 (
    echo [ERROR] Python 3.8 or higher is required. Found version !PYTHON_VERSION!
    pause
    exit /b 1
)

echo [*] Python !PYTHON_VERSION! detected

:: Create a virtual environment
echo [*] Creating virtual environment...
if exist "venv" (
    echo [*] Virtual environment already exists. Recreating...
    rmdir /s /q venv
)
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

:: Activate the virtual environment and install packages
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

echo [*] Upgrading pip...
python -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Failed to upgrade pip. Continuing with existing version...
)

:: Install requirements
echo [*] Installing required packages (this may take a few minutes)...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install required packages.
    pause
    exit /b 1
)

:: Create .env file if it doesn't exist
if not exist ".env" (
    echo [*] Creating .env file...
    copy /Y .env.example .env >nul
    
    :: Generate a secure secret key
    echo [*] Generating a secure secret key...
    for /f "delims=" %%a in ('python -c "import secrets; print(secrets.token_hex(24))"') do set SECRET_KEY=%%a
    
    :: Update the .env file with the generated secret key
    echo [*] Updating .env with generated secret key...
    powershell -Command "(Get-Content .env) -replace 'SECRET_KEY=.*', 'SECRET_KEY=!SECRET_KEY!' | Set-Content .env"
    
    echo [*] .env file has been created. Please review and update the configuration as needed.
) else (
    echo [*] .env file already exists. Skipping creation.
)

:: Create uploads directory if it doesn't exist
if not exist "uploads" (
    echo [*] Creating uploads directory...
    mkdir uploads
)

:: Initialize the database
echo [*] Initializing the database...
python init_db.py
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Database initialization completed with warnings.
)

echo.
echo ============================================
echo   Setup completed successfully!
echo ============================================
echo.
echo [*] To start the application in development mode:
echo     run_app.bat
echo.
echo [*] To create an admin user:
echo     python init_db.py
echo.
echo [*] For production deployment, please:
echo     1. Update .env with production settings
echo     2. Set FLASK_ENV=production
echo     3. Configure a production WSGI server
echo.
pause

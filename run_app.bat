@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: ====================================
:: Run Script for Snowsports Program Manager
:: ====================================

echo ############################################
echo #  Starting Snowsports Program Manager  #
echo ############################################
echo.

:: Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo.
    echo Please run setup.bat first to set up the development environment.
    pause
    exit /b 1
)

:: Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found. Creating from example...
    if exist ".env.example" (
        copy /Y .env.example .env >nul
        echo [*] Created .env file from example. Please review and update the configuration.
    ) else (
        echo [ERROR] .env.example not found. Cannot create .env file.
        pause
        exit /b 1
    )
)

:: Check if SECRET_KEY is set in .env
findstr /i /c:"SECRET_KEY=" .env >nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] SECRET_KEY is not set in .env. Generating a secure key...
    for /f "delims=" %%a in ('python -c "import secrets; print(secrets.token_hex(24))"') do set SECRET_KEY=%%a
    echo SECRET_KEY=!SECRET_KEY!>> .env
    echo [*] Added SECRET_KEY to .env
)

:: Activate the virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Set environment variables
echo [*] Setting up environment...
set FLASK_APP=run.py
set FLASK_ENV=development

:: Check if database needs to be initialized
if not exist "instance\app.db" (
    echo [*] Database not found. Initializing database...
    python init_db.py
    if %ERRORLEVEL% NEQ 0 (
        echo [WARNING] Database initialization completed with warnings.
    )
)

:: Run database migrations
echo [*] Checking for database migrations...
flask db upgrade
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Database migration completed with warnings.
)

:: Start the Flask development server
echo.
echo ============================================
echo   Starting Snowsports Program Manager...
echo ============================================
echo.
echo [*] Application URL: http://127.0.0.1:5000
echo [*] Press Ctrl+C to stop the server
echo.

python -m flask run --host=0.0.0.0 --port=5000

:: Check if the Flask application exited with an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] The application has stopped with an error.
    echo.
    pause
)

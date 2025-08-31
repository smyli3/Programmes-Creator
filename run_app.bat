@echo off
echo Starting Snowsports Program Manager...

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate the virtual environment and run the app
call venv\Scripts\activate.bat
python app.py

REM Keep the window open if there's an error
if %ERRORLEVEL% NEQ 0 pause

@echo off
echo Checking Python installation...
"C:\Users\Adam Smylie\AppData\Local\Programs\Python\Python313\python.exe" --version
if %errorlevel% neq 0 (
    echo Python is not working properly.
    exit /b 1
)

echo.
echo Installing required packages...
"C:\Users\Adam Smylie\AppData\Local\Programs\Python\Python313\python.exe" -m pip install --upgrade pip
"C:\Users\Adam Smylie\AppData\Local\Programs\Python\Python313\python.exe" -m pip install pandas openpyxl xlrd

if %errorlevel% neq 0 (
    echo Failed to install required packages.
    exit /b 1
)

echo.
echo Running the analysis script...
"C:\Users\Adam Smylie\AppData\Local\Programs\Python\Python313\python.exe" analyze_program.py

if %errorlevel% neq 0 (
    echo.
    echo Analysis script failed to run.
    pause
)

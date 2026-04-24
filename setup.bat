@echo off
echo ==============================
echo   AI Drawing App Setup Start
echo ==============================

:: Check Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python not found! Please install Python and try again.
    pause
    exit
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv

:: Activate venv
call venv\Scripts\activate

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo Installing dependencies...
python -m pip install -r requirements.txt

echo ==============================
echo   Setup Completed Successfully!
echo ==============================

pause

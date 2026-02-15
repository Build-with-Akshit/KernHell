@echo off
setlocal EnableDelayedExpansion

echo ===========================================
echo       KernHell - Global Setup
echo ===========================================

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Install the Package Globally
echo [INFO] Installing KernHell globally...
pip install .

REM Install Playwright Browsers
echo [INFO] Installing Playwright browsers...
playwright install

echo.
echo ===========================================
echo [SUCCESS] KernHell installed successfully!
echo.
echo You can now run it from anywhere using:
echo   kernhell --help
echo   kernhell heal <script.py>
echo.
echo Don't forget to set your GEMINI_API_KEY environment variable.
echo ===========================================
pause

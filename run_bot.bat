@echo off

set PROJECT_DIR=C:\Users\aswin.m\Desktop\auto-trade-options

set LOG_DIR=%PROJECT_DIR%\logs

if not exist "%LOG_DIR%" (
mkdir "%LOG_DIR%"
)

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy_MM_dd_HH_mm_ss"') do set TIMESTAMP=%%i

set LOG_FILE=%LOG_DIR%\bot_%TIMESTAMP%.log

cd /d "%PROJECT_DIR%"

call venv\Scripts\activate

python main.py >> "%LOG_FILE%" 2>&1

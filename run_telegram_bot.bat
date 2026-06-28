@echo off
cd /d "%~dp0"

call venv\Scripts\activate.bat

python token_generation\telegram_bot.py

pause


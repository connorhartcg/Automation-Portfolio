@echo off
cd /d "C:\Users\drgre\OneDrive\Documents\Automation\credentials"
call .venv\Scripts\activate.bat
python replace_source_sheet.py
pause
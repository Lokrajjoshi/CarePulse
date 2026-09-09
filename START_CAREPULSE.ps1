$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path '.venv\Scripts\python.exe')) { python -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe scripts\initialise_database.py
if (-not (Test-Path 'carepulse_demo.db')) { & .\.venv\Scripts\python.exe scripts\reset_demo.py }
Write-Host 'CarePulse is starting at http://127.0.0.1:8000. Stop with Ctrl+C.'
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload


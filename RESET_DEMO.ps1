$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path '.venv\Scripts\python.exe')) { Write-Error 'Create the virtual environment first: python -m venv .venv' }
& .\.venv\Scripts\python.exe scripts\reset_demo.py


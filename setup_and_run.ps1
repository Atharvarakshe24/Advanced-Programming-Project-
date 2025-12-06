# Setup and run script for Scholar's Digital Library
# Creates a virtual environment, installs requirements, starts server and GUI
Set-StrictMode -Version Latest
$proj = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
Set-Location $proj

Write-Host "[1/5] Creating virtual environment .venv (if missing)..."
python -m venv .venv

$venvPython = Join-Path $proj ".venv\Scripts\python.exe"
$venvPip = Join-Path $proj ".venv\Scripts\pip.exe"

if (-Not (Test-Path $venvPython)) {
    Write-Host "Virtual environment python not found; ensure Python is on PATH and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host "[2/5] Upgrading pip and installing requirements..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

Write-Host "[3/5] Starting backend server (Flask) in a new process..."
Start-Process -FilePath $venvPython -ArgumentList 'server.py' -WorkingDirectory $proj

Start-Sleep -Seconds 1
Write-Host "[4/5] Starting GUI (Tkinter) in a new process..."
Start-Process -FilePath $venvPython -ArgumentList 'main.py' -WorkingDirectory $proj

Write-Host "[5/5] Setup complete. If windows were blocked, check PowerShell execution policy or run the commands manually." -ForegroundColor Green
Write-Host "If the GUI doesn't open, try running in two separate terminals:\n  1) $venvPython server.py\n  2) $venvPython main.py"

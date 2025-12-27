$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Host "Python is required. Install Python 3.10+ and try again."
  exit 1
}

if (-not (Test-Path ".\.venv")) {
  python -m venv .venv
}

& .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip | Out-Null
python -m pip install -r requirements.txt | Out-Null

if (-not (Test-Path ".\.env") -and (Test-Path ".\.env.example")) {
  Copy-Item ".\.env.example" ".\.env"
  Write-Host "Created .env from .env.example (please edit and set ANTHROPIC_API_KEY)."
}

python app.py


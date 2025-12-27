#!/usr/bin/env bash
set -euo pipefail

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required. Install Python 3.10+ and try again."
  exit 1
fi

if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv || {
    echo "Failed to create venv. On Ubuntu/Debian you may need: sudo apt install python3-venv"
    exit 1
  }
fi

source .venv/bin/activate
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements.txt

if [[ ! -f ".env" && -f ".env.example" ]]; then
  cp .env.example .env
  echo "Created .env from .env.example (please edit and set ANTHROPIC_API_KEY)."
fi

python app.py

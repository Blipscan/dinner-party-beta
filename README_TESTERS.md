## Dinner Party Beta (Tester Package)

This is a small local web app. You run it on your computer and open it in your browser.

### What you need
- **Option A (recommended): Docker Desktop** (works on Mac/Windows/Linux)
- **Option B: Python 3.10+** and the ability to install Python packages

### Option A — Run with Docker (fastest)
1. Install Docker Desktop (if you don't already have it).
2. Unzip this package.
3. (Recommended) Create a `.env` file for your API key:

```bash
cp .env.example .env
```

4. Edit `.env` and set **ANTHROPIC_API_KEY**.
5. Start the app (from the unzipped folder):

```bash
docker compose up --build
```

6. Open:
- http://localhost:5000

To stop:

```bash
docker compose down
```

### Option B — Run with Python
1. Unzip this package.
2. Run the one-command launcher:

**Mac/Linux**

```bash
./run_local.sh
```

**Windows (PowerShell)**

```powershell
.\run_local.ps1
```

The first run will create `.env` from `.env.example`. Edit `.env` and set **ANTHROPIC_API_KEY**, then re-run the launcher.

### Manual Python steps (if you prefer)
In a terminal in the unzipped folder, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env` and set **ANTHROPIC_API_KEY**, and start the app:

```bash
python app.py
```

5. Open:
- http://localhost:5000

### Notes
- The app will load without an API key, but **ANTHROPIC_API_KEY is required** for menu/cookbook generation.
- **BETA_ACCESS_CODE** is optional; if you don't set it, the app uses `THAMES_CLUB_VIP`.

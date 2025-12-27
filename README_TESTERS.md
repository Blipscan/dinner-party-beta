## Dinner Party Beta (Tester Package)

This is a small local web app. You run it on your computer and open it in your browser.

### What you need
- **Option A (recommended): Docker Desktop** (works on Mac/Windows/Linux)
- **Option B: Python 3.10+** and the ability to install Python packages

### Option A — Run with Docker (fastest)
1. Install Docker Desktop (if you don't already have it).
2. Unzip this package.
3. In a terminal in the unzipped folder, run:

```bash
cp .env.example .env
```

4. Edit `.env` and set **ANTHROPIC_API_KEY**.
5. Start the app:

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
2. In a terminal in the unzipped folder, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

3. Edit `.env` and set **ANTHROPIC_API_KEY**.
4. Start the app:

```bash
python app.py
```

5. Open:
- http://localhost:5000

### Notes
- **ANTHROPIC_API_KEY is required** for menu/cookbook generation.
- **BETA_ACCESS_CODE** is optional; if you don't set it, the app uses `THAMES_CLUB_VIP`.

# Visa Rule Watchdog

**Your visa requirements change. Your checklist should too.**

Built at HackIIITD 2026 (ESYA '26, IIIT Delhi) by **Team Civic Sentinels**.

Visa Rule Watchdog is an AI agent that tracks official visa-rule changes and tells a traveller exactly which documents they need, with the **source passage and timestamp as proof**.

## The problem

Visa rules are scattered across embassy and immigration websites and change without notice. Travellers rely on saved notes and blog posts that quietly go stale, and cannot tell whether a change affects them.

## How it works

1. The user enters nationality, destination, visa type and travel date.
2. TinyFish Search finds official embassy / immigration pages.
3. TinyFish Fetch reads each page.
4. An LLM extracts structured requirement items, each with a verbatim source passage.
5. Items without a quotable passage are dropped. Nothing is invented.
6. Items are saved as snapshots in SQLite.
7. A re-check (manual refresh) compares new items with the old ones.
8. Changes show up as alerts with old vs new values and the source passage.

## Design rules

1. Every checklist item stores its source URL, retrieval timestamp and verbatim passage.
2. If the LLM cannot quote a passage, the item is dropped.
3. Diffs run on structured items, not raw page text, to avoid false alerts.
4. Blocked or unreachable pages show a visible "could not verify" state. We never guess.
5. The demo uses a clearly labelled SIMULATED change.
6. MVP scope: nationality India, student visa, destinations Germany, UK and Canada.

## Tech stack

- Backend: Python 3.11+, FastAPI, SQLite (SQLAlchemy)
- Auth: JWT (python-jose) and bcrypt (passlib)
- External: TinyFish API (Search, Fetch) and an LLM API for extraction
- Frontend: React (Vite)
- Secrets: `.env` files only, never committed

## Project structure

```
VisaRuleWatchdog_v0.0/
  backend/
    app/
      main.py, config.py, database.py, models.py, schemas.py
      routers/   auth, trips, alerts, demo, checklist
      services/  tinyfish, extractor, differ
    requirements.txt
  frontend/            React + Vite app
  README.md
```

## Run locally (Windows PowerShell)

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for the API docs.

Create `backend/.env` with your own keys:

```
TINYFISH_API_KEY=your_key_here
SECRET_KEY=your_secret_here
```

Add the LLM API key variable that `backend/app/config.py` expects.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

Create `frontend/.env`:

```
VITE_API_URL=http://127.0.0.1:8000
VITE_USE_MOCK=false
```

Set `VITE_USE_MOCK=true` to run the UI on sample data without the backend.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /auth/register | Create account |
| POST | /auth/login | Get JWT |
| POST | /trips | Create trip, then search, fetch, extract |
| GET | /trips/{id} | Trip with its sources |
| GET | /trips/{id}/checklist | Checklist with passages |
| POST | /trips/{id}/refresh | Manual re-check |
| GET | /trips/{id}/changes | Old vs new changes |
| GET | /alerts | Alert feed |
| PATCH | /checklist/{item_id} | Mark done or pending |
| POST | /demo/simulate-change?trip_id=N | Inject a labelled SIMULATED change |

## Status and known limitations

- Backend pipeline (search, fetch, extract, diff, alerts) is working. Creating a trip takes about 1-2 minutes.
- Trips, alerts and checklist routes are not yet login-protected (a temporary user id is used).
- No scheduler yet: re-checks are manual only.
- The simulated change adds a change and an alert, but does not yet add the item to the checklist.
- The `demo-mock` branch shows a polished UI on **static sample data**, clearly labelled SAMPLE DATA. It is for demonstration only.
- Connecting the live checklist page to the backend is still in progress.

## Responsible design

- Official government and embassy sources only.
- Source links and last-checked times are always shown.
- Uncertain or unverifiable information is labelled, never guessed.
- No passport or ID numbers are stored.
- This tool is not legal or immigration advice. Always confirm with the official source before applying.

## Team

Civic Sentinels: Kinjal Singla, Arushi Das, Nidhi Jha

# Preliminary Design Report (PDR)
## Visa Rule Watchdog
**Team:** Civic Sentinels | **Event:** HackIIITD 2026 | **Version:** 1.0
 
---
 
## 1. Purpose
This document describes the technical design of Visa Rule Watchdog: architecture, stack, data model, API, key algorithms, security, and the 24-hour build plan. It complements the PRD.
 
## 2. Technology Stack
| Layer | Choice | Notes |
|---|---|---|
| Backend | Python 3.11+, FastAPI | REST API, orchestration |
| Database | SQLite via SQLAlchemy | Simple, file-based, good for MVP |
| Scheduler | APScheduler | Periodic re-fetch jobs |
| Frontend | React (Vite) | Streamlit only if the team decides to switch |
| Auth | JWT (python-jose) + passlib/bcrypt | Stateless tokens, hashed passwords |
| External | TinyFish API (Search, Fetch, Agent) | Confirm exact endpoints and parameters in the official TinyFish docs |
| LLM | LLM API for extraction | Output must be strict JSON with passages |
| Secrets | `.env` file | Never committed to git |
 
## 3. System Architecture
 
```
React UI (trip form, checklist, diff view, alert feed, dashboard)
        |  REST (JSON, JWT)
FastAPI backend
  |-- Auth router
  |-- Trips router --> orchestrates the pipeline
  |-- Alerts router
  |-- Demo router (simulated change)
  |
  |-- services/tinyfish.py   (Search, Fetch, Agent wrapper)
  |-- services/extractor.py  (LLM -> structured items + passages)
  |-- services/differ.py     (item-level compare)
  |-- services/scheduler.py  (APScheduler jobs)
  |
SQLite (users, trips, sources, snapshots, checklist_items, changes, alerts)
```
 
## 4. Core Pipeline
1. **Create trip:** the user submits nationality, destination, visa type, travel date.
2. **Search:** TinyFish Search finds official embassy or immigration URLs; store ranked results in `sources`.
3. **Fetch:** TinyFish Fetch reads each page; save raw text with `fetched_at`.
4. **Extract:** the LLM converts text into structured items (name, required, fee, deadline, passage). Items without a verbatim passage are discarded.
5. **Validate:** check that each passage actually appears in the fetched text (substring or fuzzy match). If not, drop the item.
6. **Save:** store the snapshot and create or update `checklist_items`.
7. **Refresh:** the scheduler or a manual call re-fetches. If the content hash is unchanged, skip extraction.
8. **Diff:** compare new items vs the previous snapshot's items and record `changes`.
9. **Alert:** create an `alerts` row; the UI shows old vs new with the source.
## 5. Key Design Rules (never violate)
1. Every checklist item stores source URL, retrieval timestamp and verbatim source passage.
2. If the LLM cannot quote a passage, drop the item. Never invent requirements.
3. Diffs run on structured items, not raw page text.
4. Blocked or unreachable pages show a visible "could not verify" state. Never guess.
5. Demo uses a clearly labelled SIMULATED change.
6. MVP corridors: 2-3 country pairs, 1-2 visa types.
## 6. Data Model
 
| Table | Columns |
|---|---|
| users | id, email, password_hash, created_at |
| trips | id, user_id, nationality, destination, visa_type, travel_date, created_at |
| sources | id, trip_id, url, rank, is_official, status (ok / blocked / error) |
| snapshots | id, source_id, content_hash, raw_text, items_json, fetched_at |
| checklist_items | id, trip_id, name, required, details, status (pending / done), source_url, passage, last_checked |
| changes | id, trip_id, item_name, change_type (added / removed / modified), old_value, new_value, passage, source_url, detected_at, is_simulated |
| alerts | id, user_id, change_id, seen, created_at |
 
## 7. API Design
 
| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| POST | /auth/register | Create account | No |
| POST | /auth/login | Get JWT | No |
| POST | /trips | Create trip and run search, fetch, extract | Yes |
| GET | /trips/{id}/checklist | Personalised checklist | Yes |
| POST | /trips/{id}/refresh | Manual re-check | Yes |
| GET | /trips/{id}/changes | Diffs, old vs new | Yes |
| GET | /alerts | Alert feed | Yes |
| PATCH | /checklist/{item_id} | Mark done or pending | Yes |
| POST | /demo/simulate-change | Inject a labelled simulated change | Yes |
 
## 8. Extraction Schema (target output from the LLM)
```json
{
  "items": [
    {
      "name": "Proof of onward travel",
      "required": true,
      "details": "Confirmed return or onward ticket",
      "passage": "Applicants must show proof of onward travel."
    }
  ]
}
```
Rules: return JSON only; `passage` must be copied verbatim from the source text; omit any item that has no passage.
 
## 9. Diff Engine Design
- Normalise item names (lowercase, trimmed) to form a key.
- Compare old vs new by key:
  - key only in new -> **added**
  - key only in old -> **removed**
  - same key with different `required`, `details` or `fee` -> **modified**
- Ignore cosmetic changes (whitespace, ordering, page layout).
- Each change stores old and new values plus the source passage.
## 10. Error Handling
| Situation | Behaviour |
|---|---|
| TinyFish Search returns nothing | Show "no official source found"; no guessed checklist |
| Fetch blocked, timed out or errored | Mark the source "could not verify" and show it in the UI |
| LLM returns invalid JSON | Retry once, then mark extraction failed |
| Passage not found in source text | Drop that item |
| Network failure during demo | Fall back to cached snapshots for demo corridors |
 
## 11. Security and Privacy
- Passwords hashed with bcrypt; JWT with expiry.
- All secrets in `.env`, listed in `.gitignore`.
- Collect only what is needed; do not store passport or ID numbers.
- CORS restricted to the frontend origin.
- Validate all inputs via Pydantic schemas.
## 12. Folder Structure
```
visa-watchdog/
  backend/
    app/
      main.py, config.py, database.py, models.py, schemas.py
      routers/   auth.py, trips.py, alerts.py, demo.py
      services/  tinyfish.py, extractor.py, differ.py, scheduler.py
    requirements.txt
    .env
  frontend/      (React + Vite)
  README.md
```
 
## 13. 24-Hour Build Plan
 
| Hours | Phase | Output |
|---|---|---|
| 0-2 | 0. Setup | Repo, environments, API keys, TinyFish test calls, corridors chosen |
| 2-5 | 1. Backend core + TinyFish | DB models, trip CRUD, Search and Fetch wrapper, snapshots |
| 5-8 | 2. Auth | Register, login, JWT, protected routes |
| 8-12 | 3. Extraction + checklist | LLM extractor with passage validation, checklist endpoint |
| 12-16 | 4. Diff + alerts + scheduler | Differ, changes, alerts, APScheduler, simulate-change endpoint |
| 12-19 | 5. Frontend | Trip form, checklist, diff view, alert feed, dashboard (parallel with phase 4) |
| 19-21 | 6. Integration + hardening | End-to-end run, error states, cached fallbacks |
| 21-24 | 7. Demo + pitch prep | Rehearsal, backup recording, README, final slides, code freeze at hour 23 |
 
**Stretch (only if ahead):** Agent portal monitoring, deadline reminders, email alerts.
 
## 14. Testing Plan
- Manual end-to-end test of the full demo loop.
- Unit tests for the differ (added, removed, modified, no change).
- Test the extractor on real pages from each demo corridor.
- Test the blocked-page path by feeding a bad URL.
- Check that no checklist item is ever saved without a passage.
## 15. Open Questions (decide in Phase 0)
- Final 2-3 country corridors and visa types.
- Which LLM API and model to use.
- TinyFish plan limits and exact endpoints (check the official docs).
- React vs Streamlit (default: React).
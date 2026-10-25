 Product Requirements Document (PRD)
## Visa Rule Watchdog
**Event:** HackIIITD 2026 (ESYA '26, IIIT Delhi)
**Team:** Civic Sentinels (Kinjal Singla, Arushi Das, Nidhi Jha)
**Version:** 1.0 | **Build window:** 24 hours
 
---
 
## 1. Overview
**Tagline:** Your visa requirements change. Your checklist should too.
 
Visa Rule Watchdog is a TinyFish-powered agent that tracks official visa-rule changes and tells a traveller exactly which documents they now need, with source passages and timestamps as proof.
 
## 2. Problem Statement
Visa requirements are published across scattered embassy, consulate and immigration websites and change without notice. Travellers rely on static checklists (saved notes, blogs, forum posts) that quietly go stale, and they cannot tell whether a change affects their nationality, visa type or travel date. This leads to repeated research, incomplete applications and possible travel delays.
 
| Pain point | Description |
|---|---|
| Scattered information | Right official pages must be found manually for each country pair and visa type |
| Outdated preparation | Forms, fees, appointment rules and supporting documents change silently |
| No personal impact check | Users cannot tell if a change affects them specifically |
 
## 3. Goals and Non-Goals
 
### Goals
- Find and read official visa-requirement pages for a user's trip.
- Produce a personalised checklist where every item is traceable to a source.
- Detect meaningful changes between saved and new requirements.
- Alert the user with old vs new values and the source passage.
### Non-Goals (MVP)
- Legal or immigration advice, or guaranteeing a visa outcome.
- Submitting visa applications on the user's behalf.
- Covering every country or visa type.
- Group or family travel monitoring.
- Payments, mobile apps, multi-language UI.
## 4. Target Users
| User | Need |
|---|---|
| Students going abroad | Track changing study-visa requirements, document lists, intake deadlines |
| Frequent and business travellers | Alerts when requirements change between trips |
| Travel agents and consultants | Monitor updates across many destinations and client checklists (post-MVP) |
 
## 5. User Stories
1. As a traveller, I enter my nationality, destination, visa type and travel date so I get a checklist for my trip.
2. As a traveller, I see the official source link, last-checked time and source passage for every item so I can trust it.
3. As a traveller, I get an alert when a requirement changes so my saved checklist does not go stale.
4. As a traveller, I see old and new requirements side by side so I understand exactly what changed.
5. As a traveller, I mark documents as done so I can track my readiness.
6. As a traveller, I am told clearly when a page could not be verified so I never rely on a guess.
7. As a traveller, I get reminders as my application deadline approaches.
## 6. Functional Requirements
 
| ID | Requirement | Priority |
|---|---|---|
| F1 | Trip form: nationality, destination, visa type, travel date | Must |
| F2 | Find official URLs via TinyFish Search; store ranked sources | Must |
| F3 | Read pages via TinyFish Fetch; store snapshot with retrieval timestamp | Must |
| F4 | LLM extracts structured requirement items, each with a verbatim source passage | Must |
| F5 | Drop any item without a quotable passage (never invent requirements) | Must |
| F6 | Personalised checklist with source URL, timestamp and passage per item | Must |
| F7 | Scheduled and manual re-fetch; item-level diff against the last snapshot | Must |
| F8 | Side-by-side old vs new view with source passage | Must |
| F9 | In-app alert feed with status ("Verified, review before applying") | Must |
| F10 | Visible "could not verify" state for blocked or unreachable pages | Must |
| F11 | User accounts: register, login (JWT) | Must |
| F12 | Readiness dashboard (done / pending items) | Should |
| F13 | Deadline reminders based on travel date | Should |
| F14 | Simulated-change demo endpoint, clearly labelled SIMULATED | Must (demo) |
| F15 | Portal monitoring (appointments, form changes) via TinyFish Agent | Could |
| F16 | Email alerts | Could |
 
## 7. Non-Functional Requirements
- **Traceability:** every item stores source URL, retrieval timestamp and verbatim passage.
- **Honesty:** low-confidence or unverifiable data is labelled uncertain, never guessed.
- **Low false alerts:** diffs run on structured items, not raw page text.
- **Privacy:** store minimal personal data; never store passport numbers; secrets only in `.env`.
- **Performance:** first checklist in roughly 60 seconds; refresh runs in the background.
- **Reliability:** cached snapshots and a fallback for demo corridors if the network fails.
## 8. MVP Scope
- 2-3 country pairs, 1-2 visa types (final list to be decided in Phase 0).
- Demo uses a clearly labelled simulated change.
### Cut order if behind schedule
1. Agent portal monitoring
2. Email alerts
3. Dashboard polish
4. Deadline reminders
**Never cut:** source passages and the diff view.
 
## 9. Success Metrics
- Full demo loop works end to end: trip -> checklist -> change -> alert -> updated list.
- 100% of checklist items have a source URL, timestamp and passage.
- 0 fabricated requirements in demo corridors.
- Blocked pages always produce a visible "could not verify" state.
## 10. Demo Scenario (about 3 minutes)
1. Enter a trip (nationality, destination, visa type, date).
2. The checklist appears with sources and timestamps.
3. Trigger the SIMULATED change (for example, "proof of onward travel" becomes required).
4. The diff flags the item; an alert shows old vs new, the source passage, and "Verified, review before applying".
5. The user updates the checklist; the dashboard shows readiness.
## 11. Responsible Design
- Use trusted government and embassy sources only.
- Show source links and last-checked dates.
- Avoid false alerts and unverified information.
- State clearly when information is uncertain.
- Protect users' personal and travel information.
## 12. Risks
| Risk | Mitigation |
|---|---|
| Official sites block automated access | TinyFish Fetch/Agent; cached snapshots; visible "could not verify" |
| LLM hallucination | Verbatim passage required; drop uncited items |
| No real change during demo | Labelled simulated change |
| API quota or latency | Cache results; background jobs |
| Scope creep | Strict MVP; cut order above |
 
## 13. Roadmap (post-hackathon)
Wider country coverage, scheduled monitoring at scale, email alerts, a test suite to cut false positives, group and family trips, agent multi-client view.
 
 
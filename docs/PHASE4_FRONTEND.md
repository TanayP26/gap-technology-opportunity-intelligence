# Phase 4 — frontend

Phase 4 turns the persisted GAP backend into a judge-facing product interface.

## Product direction

The interface is intentionally closer to a research instrument than a generic AI dashboard:

- dark neutral surfaces
- small radii and restrained motion
- evidence-first copy
- no chatbot shell
- no invented company logos, testimonials, or synthetic metrics
- scores stay secondary to their underlying source signals

## Routes

`/`

Discover. Accepts a technology, geography, and 2–8 subdomains and calls the real `POST /api/v1/analyses` endpoint.

`/analysis/{analysis_id}`

Technology landscape. Fetches the persisted analysis and ranked landscape. The chart uses:

- x: visible market presence
- y: technical momentum
- bubble size: demand momentum
- opacity: confidence

The accessible table exposes all five source signals, confidence, GAP score, and evidence counts.

`/analysis/{analysis_id}/subdomain/{subdomain_id}`

Signal and evidence inspection. Evidence filters map directly to the persisted evidence endpoint.

`/analysis/{analysis_id}/graph`

A provenance-only graph built from persisted evidence. Edges mean “belongs to this subdomain’s retrieved evidence set”; they do not imply causality or semantic similarity.

## Run

Backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8050
```

Frontend:

```powershell
cd frontend
Copy-Item .env.local.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`.

The backend default CORS origin already allows `http://localhost:3000`.

## Demo path

Use the Neuromorphic Computing setup, run the analysis once, open the ranked landscape, inspect Event-Based Vision, then open its evidence and the provenance graph. This keeps the demo centered on “see where the signals don’t agree” rather than on infrastructure.

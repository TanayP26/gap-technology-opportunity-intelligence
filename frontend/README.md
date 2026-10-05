# GAP frontend

Next.js + TypeScript interface for the GAP Phase 3.1 API.

## Run

```powershell
cd frontend
Copy-Item .env.local.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`.

The backend should be running on `http://127.0.0.1:8050`.

## Screens

- `/` — Discover / create analysis
- `/analysis/{id}` — ranked technology landscape
- `/analysis/{id}/subdomain/{subdomainId}` — signal and evidence inspection
- `/analysis/{id}/graph` — evidence provenance graph derived from persisted evidence

The frontend does not recompute GAP scores. The API remains the source of truth.

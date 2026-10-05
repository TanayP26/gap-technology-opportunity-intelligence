# API contract

Base path: `/api/v1`

## Implemented in starter

### `GET /health`

Returns service status.

### `POST /api/v1/analyses/preview`

Used during engineering to inspect the exact SerpApi plan before spending credits.

Request:

```json
{
  "technology": "Neuromorphic computing",
  "subdomains": [
    "Spiking neural networks",
    "Neuromorphic processors",
    "Memristive computing",
    "Event-based vision",
    "Neuromorphic sensors",
    "On-device learning"
  ],
  "geography": "Worldwide"
}
```

Response includes every planned query and `estimated_serpapi_calls`.

### `POST /api/v1/analyses/score`

Engineering-only scoring endpoint. It makes formula work testable before orchestration exists.

## Production MVP endpoints

### `POST /api/v1/analyses`

Create an analysis.

Request:

```json
{
  "technology": "Neuromorphic computing",
  "geography": "Worldwide"
}
```

Response:

```json
{
  "id": "uuid",
  "technology": "Neuromorphic computing",
  "status": "draft"
}
```

### `POST /api/v1/analyses/{analysis_id}/run`

Generates/accepts taxonomy, creates query plan, executes retrieval, normalizes evidence, and computes signals.

Return `202 Accepted` once persistence exists. The frontend can poll status every 1-2 seconds during the demo. Do not add WebSockets unless polling becomes visibly bad.

### `GET /api/v1/analyses/{analysis_id}`

Returns lifecycle status, subdomains, source completion, and high-level counts.

### `GET /api/v1/analyses/{analysis_id}/landscape`

Returns one compact row per subdomain:

```json
{
  "analysis_id": "uuid",
  "subdomains": [
    {
      "id": "uuid",
      "name": "Memristive computing",
      "research": 0.88,
      "patents": 0.74,
      "attention": 0.69,
      "events": 0.41,
      "market": 0.24,
      "confidence": 0.82,
      "technical_momentum": 0.817,
      "demand_momentum": 0.564,
      "gap_score": 0.287
    }
  ]
}
```

The frontend derives x/y/bubble values from these fields; the backend remains the source of truth for scores.

### `GET /api/v1/subdomains/{subdomain_id}`

Returns detailed signals, explanation, formula version, source statuses, and timestamps.

### `GET /api/v1/subdomains/{subdomain_id}/evidence?type=paper`

Paginated normalized evidence.

### `GET /api/v1/analyses/{analysis_id}/graph`

Returns nodes and edges that can be traced to normalized evidence.

## Error shape

All custom errors use:

```json
{
  "error": {
    "code": "SERPAPI_RATE_LIMIT",
    "message": "Search provider quota is temporarily unavailable.",
    "retryable": true
  }
}
```

Do not leak upstream API keys, raw stack traces, or full query URLs containing credentials.

## Scoring integrity

A failed source is represented as unavailable evidence, not as a zero-valued signal. For example,
if the market-presence search fails, `market` is `null` rather than `0.0`. In that case the score is:

```json
{
  "status": "insufficient_evidence",
  "missing_signals": ["market"],
  "technical_momentum": null,
  "demand_momentum": null,
  "whitespace": null,
  "gap_score": null
}
```

A successful source with zero results is still a real zero and may be scored normally. Landscape
responses keep incomplete entries but place them after scored entries.

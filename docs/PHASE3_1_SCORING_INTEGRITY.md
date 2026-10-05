# Phase 3.1 — Scoring integrity

GAP no longer interprets a failed SerpApi source as a zero-valued market signal.

For each subdomain, the five scoring signals are now nullable. A signal is `null` only when
the source needed to derive it did not complete successfully. A successful source with zero
results still produces a legitimate `0.0` signal.

If any scoring signal is unavailable:

- `score.status` is `insufficient_evidence`
- `score.missing_signals` names the unavailable signals
- `technical_momentum`, `demand_momentum`, `whitespace`, and `gap_score` are `null`
- the incomplete entry is retained in the analysis and placed after scored entries in the landscape
- confidence is reduced by source coverage

This prevents a temporary source outage from looking like market whitespace.

Apply `db/003_scoring_integrity.sql` before running Phase 3.1.

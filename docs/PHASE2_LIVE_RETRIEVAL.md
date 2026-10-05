# Phase 2 — live retrieval

Phase 2 adds a deliberately small live slice before the full analysis runner.

`POST /api/v1/analyses/probe` runs one subdomain through all five SerpApi sources. It is intentionally guarded by `confirm_live_search=true` because a cold probe plans seven searches.

The probe exists to verify three things before we spend credits on a six-subdomain analysis:

1. the API key is loaded;
2. response shapes still match our normalizers;
3. the signal engine behaves sensibly on real evidence.

Raw SerpApi responses are cached under `backend/.cache/serpapi`. The cache key is a SHA-256 fingerprint of engine + request parameters, never the API key. Cache TTLs differ by source because news changes much faster than patents.

## Method note

Scholar and Patents `search_information.total_results` are treated as approximate retrieval signals, not exact publication or patent census counts. They are used only for directional momentum. The UI must not describe them as authoritative totals.

Google Trends values are used for within-query temporal momentum. Do not compare raw Trends values across different batches as if they were absolute popularity measures.

## Failure policy

One failed source does not fail the whole probe. The run records the source error and confidence falls because evidence coverage is lower. This is intentional; Google News is allowed to fail without erasing valid Scholar, Patent, Search, or Trends evidence.

# Phase 3: persisted technology landscapes

Phase 3 changes GAP from a single-subdomain integration probe into a persisted multi-subdomain analysis service.

## Request lifecycle

1. Validate the technology and 2–8 unique subdomains.
2. Create an `analyses` row and ordered `subdomains` rows.
3. Build the SerpApi query plan.
4. Execute the plan through the Phase 2 cache and concurrency controls.
5. Derive each subdomain's signals using only search runs that target that subdomain.
6. Persist search run audit rows, normalized evidence, trend points, and a `gap-v1` signal snapshot.
7. Mark the analysis complete.
8. Return the persisted representation rather than an in-memory copy.

## Why target identity was added to planned searches

The Phase 2 scorer worked for one subdomain because every source run belonged to that one target. A full landscape cannot safely sum every Scholar or Patent result across the entire technology. `PlannedSearch.target_subdomains` and `SearchRunResult.target_subdomains` keep that provenance explicit. Google Trends may target up to five subdomains in one request; the other signal searches target one.

## Cache versus persistence

The local cache avoids unnecessary SerpApi calls. PostgreSQL serves a different purpose: it records what an analysis used. A cache hit is still written to `search_runs` with status `cached`, so the final landscape remains auditable.

## Fingerprint migration

The original schema used a partial unique index on successful search fingerprints. That prevents the same cached search from appearing in two separate analyses. `002_phase3.sql` removes the uniqueness constraint and keeps a normal fingerprint index instead.

## Evidence dates

SerpApi sources expose dates in different formats. GAP stores a timestamp only when it can parse one deterministically. If a source returns a human string such as `3 hours ago`, the raw value is retained in evidence metadata rather than inventing a timestamp.

## Failure behavior

Individual SerpApi source failures are retained as `search_runs.status = error` and reduce cross-source confidence naturally. A database or orchestration failure marks the overall analysis as failed. GAP does not silently replace missing source data.

## Formula version

Phase 3 stores snapshots under `gap-v1`. The current formula remains a product heuristic and should be calibrated before strong claims are made from absolute score values.

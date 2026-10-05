-- Phase 3 turns search_runs into an analysis audit log.
-- The same cached search may legitimately be reused by more than one analysis,
-- so query fingerprints must be indexed, not globally unique.

DROP INDEX IF EXISTS search_runs_fingerprint_success_idx;

CREATE INDEX IF NOT EXISTS search_runs_fingerprint_idx
    ON search_runs(query_fingerprint);

CREATE INDEX IF NOT EXISTS search_runs_subdomain_status_idx
    ON search_runs(subdomain_id, status);

CREATE INDEX IF NOT EXISTS evidence_subdomain_published_idx
    ON evidence_items(subdomain_id, published_at DESC);

CREATE INDEX IF NOT EXISTS signal_snapshots_subdomain_created_idx
    ON signal_snapshots(subdomain_id, created_at DESC);

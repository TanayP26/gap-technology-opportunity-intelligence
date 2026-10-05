CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE analyses (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    technology text NOT NULL,
    geography text NOT NULL DEFAULT 'Worldwide',
    status text NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'planned', 'running', 'complete', 'failed')),
    created_at timestamptz NOT NULL DEFAULT now(),
    started_at timestamptz,
    completed_at timestamptz,
    failure_reason text
);

CREATE TABLE subdomains (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id uuid NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    name text NOT NULL,
    slug text NOT NULL,
    description text,
    position integer NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (analysis_id, slug)
);

CREATE TABLE search_runs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id uuid NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    subdomain_id uuid REFERENCES subdomains(id) ON DELETE CASCADE,
    engine text NOT NULL,
    purpose text NOT NULL,
    query text NOT NULL,
    params jsonb NOT NULL DEFAULT '{}'::jsonb,
    query_fingerprint text NOT NULL,
    status text NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'running', 'success', 'error', 'cached')),
    serpapi_search_id text,
    result_count integer,
    response_json jsonb,
    error_message text,
    created_at timestamptz NOT NULL DEFAULT now(),
    completed_at timestamptz
);

CREATE UNIQUE INDEX search_runs_fingerprint_success_idx
    ON search_runs(query_fingerprint)
    WHERE status IN ('success', 'cached');

CREATE INDEX search_runs_analysis_idx ON search_runs(analysis_id);
CREATE INDEX search_runs_subdomain_idx ON search_runs(subdomain_id);

CREATE TABLE evidence_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id uuid NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    subdomain_id uuid NOT NULL REFERENCES subdomains(id) ON DELETE CASCADE,
    search_run_id uuid REFERENCES search_runs(id) ON DELETE SET NULL,
    evidence_type text NOT NULL
        CHECK (evidence_type IN ('paper', 'patent', 'news', 'market')),
    title text NOT NULL,
    url text,
    source_name text,
    published_at timestamptz,
    snippet text,
    external_id text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX evidence_analysis_idx ON evidence_items(analysis_id);
CREATE INDEX evidence_subdomain_idx ON evidence_items(subdomain_id);
CREATE INDEX evidence_type_idx ON evidence_items(evidence_type);
CREATE INDEX evidence_external_id_idx ON evidence_items(external_id);

CREATE TABLE trend_points (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id uuid NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    subdomain_id uuid NOT NULL REFERENCES subdomains(id) ON DELETE CASCADE,
    observed_at timestamptz NOT NULL,
    value numeric(6,2) NOT NULL CHECK (value >= 0),
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (subdomain_id, observed_at)
);

CREATE INDEX trend_points_subdomain_time_idx
    ON trend_points(subdomain_id, observed_at);

CREATE TABLE signal_snapshots (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id uuid NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    subdomain_id uuid NOT NULL REFERENCES subdomains(id) ON DELETE CASCADE,
    research numeric(6,5) NOT NULL CHECK (research BETWEEN 0 AND 1),
    patents numeric(6,5) NOT NULL CHECK (patents BETWEEN 0 AND 1),
    attention numeric(6,5) NOT NULL CHECK (attention BETWEEN 0 AND 1),
    events numeric(6,5) NOT NULL CHECK (events BETWEEN 0 AND 1),
    market numeric(6,5) NOT NULL CHECK (market BETWEEN 0 AND 1),
    confidence numeric(6,5) NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    technical_momentum numeric(6,5) NOT NULL CHECK (technical_momentum BETWEEN 0 AND 1),
    demand_momentum numeric(6,5) NOT NULL CHECK (demand_momentum BETWEEN 0 AND 1),
    whitespace numeric(6,5) NOT NULL CHECK (whitespace BETWEEN 0 AND 1),
    gap_score numeric(6,5) NOT NULL CHECK (gap_score BETWEEN 0 AND 1),
    formula_version text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX signal_latest_version_idx
    ON signal_snapshots(subdomain_id, formula_version, created_at);

CREATE TABLE gap_hypotheses (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id uuid NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    subdomain_id uuid NOT NULL REFERENCES subdomains(id) ON DELETE CASCADE,
    title text NOT NULL,
    summary text NOT NULL,
    status text NOT NULL DEFAULT 'candidate'
        CHECK (status IN ('candidate', 'supported', 'weak_evidence', 'dismissed')),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE hypothesis_evidence (
    hypothesis_id uuid NOT NULL REFERENCES gap_hypotheses(id) ON DELETE CASCADE,
    evidence_id uuid NOT NULL REFERENCES evidence_items(id) ON DELETE CASCADE,
    relationship text NOT NULL
        CHECK (relationship IN ('supports', 'contradicts', 'context')),
    PRIMARY KEY (hypothesis_id, evidence_id)
);

CREATE TABLE entities (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id uuid NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    entity_type text NOT NULL
        CHECK (entity_type IN ('technology', 'organization', 'company', 'person', 'paper', 'patent', 'product')),
    canonical_name text NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX entities_analysis_type_idx ON entities(analysis_id, entity_type);

CREATE TABLE entity_aliases (
    entity_id uuid NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    alias text NOT NULL,
    PRIMARY KEY (entity_id, alias)
);

CREATE TABLE entity_edges (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id uuid NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    source_entity_id uuid NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    target_entity_id uuid NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    relation text NOT NULL,
    evidence_id uuid REFERENCES evidence_items(id) ON DELETE SET NULL,
    confidence numeric(6,5) NOT NULL DEFAULT 1.0 CHECK (confidence BETWEEN 0 AND 1),
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (source_entity_id <> target_entity_id)
);

CREATE INDEX entity_edges_analysis_idx ON entity_edges(analysis_id);
CREATE INDEX entity_edges_source_idx ON entity_edges(source_entity_id);
CREATE INDEX entity_edges_target_idx ON entity_edges(target_entity_id);

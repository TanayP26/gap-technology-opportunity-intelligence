-- A failed source is unknown evidence, not evidence of zero activity.
-- Allow incomplete signal snapshots to be stored without manufacturing a GAP score.

ALTER TABLE signal_snapshots
    ALTER COLUMN research DROP NOT NULL,
    ALTER COLUMN patents DROP NOT NULL,
    ALTER COLUMN attention DROP NOT NULL,
    ALTER COLUMN events DROP NOT NULL,
    ALTER COLUMN market DROP NOT NULL,
    ALTER COLUMN technical_momentum DROP NOT NULL,
    ALTER COLUMN demand_momentum DROP NOT NULL,
    ALTER COLUMN whitespace DROP NOT NULL,
    ALTER COLUMN gap_score DROP NOT NULL;

ALTER TABLE signal_snapshots
    ADD COLUMN IF NOT EXISTS score_status text NOT NULL DEFAULT 'scored'
        CHECK (score_status IN ('scored', 'insufficient_evidence')),
    ADD COLUMN IF NOT EXISTS missing_signals jsonb NOT NULL DEFAULT '[]'::jsonb;

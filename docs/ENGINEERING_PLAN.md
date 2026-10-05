# GAP engineering plan

This is the build order for the hackathon version. The rule is simple: every day ends with something runnable.

## Product boundary

GAP accepts one technology, breaks it into 4-8 subdomains, retrieves evidence from five SerpApi engines, computes transparent signals, and surfaces candidate divergence worth investigating.

The MVP does not include auth, billing, teams, chat, PDF export, notifications, admin panels, or background monitoring.

## Pipeline

1. Technology input
2. Taxonomy proposal
3. User-visible subdomain set
4. Query plan
5. Cached SerpApi retrieval
6. Result normalization
7. Signal extraction
8. Gap score + confidence
9. Evidence-backed explanation
10. Landscape and evidence UI

The LLM may help with steps 2 and 9. It must not calculate the core signals.

## Build sequence: Oct 2-10

### Oct 2 - contract and math

- Freeze schemas and names.
- Create FastAPI service.
- Implement query planner.
- Implement deterministic signal functions and unit tests.
- Freeze PostgreSQL schema.

Exit condition: `/health`, `/api/v1/analyses/preview`, and `/api/v1/analyses/score` work locally.

### Oct 3 - live retrieval

- Add SerpApi execution service.
- Add SHA-256 request fingerprinting.
- Persist `search_runs`.
- Normalize Scholar, Patents, Search, News, and Trends responses.
- Add fixture-based parser tests so development does not burn API credits.

Exit condition: one manually supplied subdomain can be retrieved and persisted end-to-end.

### Oct 4 - analysis orchestration

- Create analysis lifecycle endpoints.
- Run subdomain queries with bounded concurrency.
- Calculate signals from stored evidence.
- Persist `signal_snapshots`.
- Failure of one source should lower confidence, not kill an entire analysis.

Exit condition: one technology with 4 subdomains completes from API request to stored scores.

### Oct 5 - taxonomy and explanation

- Add taxonomy provider behind an interface.
- Keep a manual fallback if the model call fails.
- Generate short evidence-grounded explanations only after scores exist.
- Store prompts/outputs only in development logs, never expose secrets.

Exit condition: user only enters the parent technology.

### Oct 6 - frontend foundation

- Next.js app shell.
- Discover screen.
- Landscape screen with matrix + subdomain table.
- No decorative animation yet.

Exit condition: live backend data renders without mocked numbers.

### Oct 7 - evidence experience

- Gap detail page.
- Trend line.
- Signal bars.
- Evidence tabs.
- Source links and retrieval timestamps.

Exit condition: every visible claim has a route back to evidence.

### Oct 8 - graph + polish

- Build only the relationships we can defend from retrieved fields.
- Add Cytoscape graph.
- Loading/error/partial-data states.
- Responsive pass.

Exit condition: demo path is stable.

### Oct 9 - evaluation and hardening

- Retrospective case-study dataset.
- Parser regression tests.
- API retry/backoff.
- README screenshots and architecture diagram.
- Fresh-machine setup test.

Exit condition: repository can be cloned and run using the README.

### Oct 10 - submission

- Record sub-3-minute local demo.
- Verify public repo and demo link in incognito.
- Document exactly where SerpApi is material to the product.
- Disclose AI tools used.
- Submit before 23:59 IST; do not leave submission for the final minutes.

## Failure policy

An analysis can be `complete` with partial data. Each source gets its own status. Missing Trends, for example, sets attention to `null` at the aggregation layer until a fallback policy is applied; it should not silently become 0.

The current scoring helpers use numeric values because the API contract is being tested in isolation. The orchestration layer must distinguish `missing` from a genuine zero signal.

## Quality rules

- No magic numbers outside a formula/config module.
- No route directly calls SerpApi.
- No LLM output is stored as evidence.
- Raw SerpApi response remains available for debugging.
- Normalized evidence is immutable for a completed search run.
- Formula changes require a new `formula_version`.
- Every parser has a saved fixture test.

# Query strategy

The query plan is intentionally small enough to fit the free development allowance while still making SerpApi central to the product.

## Default analysis: 6 subdomains

Per subdomain:

- Google Scholar: baseline window + recent window = 2 calls
- Google Patents: baseline window + recent window = 2 calls
- Google News: recent commercial/event query = 1 call
- Google Search: market-presence query = 1 call

Google Trends accepts up to five queries in one time-series comparison, so six subdomains need two Trends calls.

Total: `6 * 6 + 2 = 38 SerpApi calls` before cache hits.

## Time windows

Baseline:

- 2022-01-01 through 2023-12-31

Recent:

- 2024-01-01 through analysis date

The two windows are converted to annualized rates before momentum is calculated. We do not compare raw counts from unequal-duration windows.

## Scholar

Purpose: research momentum.

Use `as_ylo`, `as_yhi`, `num=20`, English results, and restricted JSON fields. Store title, link, publication info, citations, and snippet.

Do not treat Google Scholar `total_results` as an exact publication count. It is a search estimate. For V1 it can be retained as metadata, while the scoring layer should prefer observed normalized results unless we explicitly validate total-count stability.

## Patents

Purpose: IP momentum.

Use publication date boundaries with `after` and `before`, `num=50`, English, and `sort=new` for the recent window. Store publication/filing dates, assignee, publication number, title, and snippet.

Deduplicate by publication number first, then patent family if we later add family metadata.

## Trends

Purpose: attention momentum.

Use `data_type=TIMESERIES` and `date=today 5-y`. Batch up to five subdomains per request. Store timestamp and extracted numeric value.

Trends values are relative interest, not absolute search volume. The UI must label them that way.

## News

Purpose: evidence of current commercial events.

Query shape:

`"subdomain" (startup OR funding OR launch OR partnership OR product)`

Sort by date. Event momentum in V1 is based on retrieved event density and recency, not a claimed total count of global news.

## Google Search

Purpose: visible market presence.

Query shape:

`"subdomain" (startup OR company OR product OR platform)`

Market presence is a heuristic derived from observed commercial-looking results. It must not be described as market share or total company count.

## Cache

Fingerprint the engine plus canonicalized parameters:

`sha256(engine + canonical_json(params))`

Recommended application TTL:

- Scholar: 48 hours
- Patents: 72 hours
- Trends: 24 hours
- News: 4 hours
- Google Search: 12 hours

SerpApi itself can return a one-hour cache for identical requests, but GAP keeps a longer application cache so repeated demos do not spend credits.

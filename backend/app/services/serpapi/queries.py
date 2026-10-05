from __future__ import annotations

from datetime import date

from app.schemas.analysis import PlannedSearch

BASELINE_START_YEAR = 2022
BASELINE_END_YEAR = 2023
RECENT_START_YEAR = 2024


def _scholar_searches(subdomain: str) -> list[PlannedSearch]:
    common = {"target_subdomains": [subdomain]}
    return [
        PlannedSearch(
            engine="google_scholar",
            purpose="research_baseline",
            query=subdomain,
            params={
                "q": subdomain,
                "as_ylo": BASELINE_START_YEAR,
                "as_yhi": BASELINE_END_YEAR,
                "num": 20,
                "hl": "en",
                "json_restrictor": (
                    "search_metadata,search_information,"
                    "organic_results[].{title,result_id,link,publication_info,"
                    "inline_links,snippet}"
                ),
            },
            **common,
        ),
        PlannedSearch(
            engine="google_scholar",
            purpose="research_recent",
            query=subdomain,
            params={
                "q": subdomain,
                "as_ylo": RECENT_START_YEAR,
                "as_yhi": date.today().year,
                "num": 20,
                "hl": "en",
                "json_restrictor": (
                    "search_metadata,search_information,"
                    "organic_results[].{title,result_id,link,publication_info,"
                    "inline_links,snippet}"
                ),
            },
            **common,
        ),
    ]


def _patent_searches(subdomain: str) -> list[PlannedSearch]:
    common = {"target_subdomains": [subdomain]}
    return [
        PlannedSearch(
            engine="google_patents",
            purpose="patent_baseline",
            query=subdomain,
            params={
                "q": f"({subdomain})",
                "after": "publication:20220101",
                "before": "publication:20231231",
                "num": 50,
                "language": "ENGLISH",
                "json_restrictor": (
                    "search_metadata,search_information,"
                    "organic_results[].{title,patent_id,patent_link,publication_date,"
                    "filing_date,priority_date,inventor,assignee,publication_number,snippet}"
                ),
            },
            **common,
        ),
        PlannedSearch(
            engine="google_patents",
            purpose="patent_recent",
            query=subdomain,
            params={
                "q": f"({subdomain})",
                "after": "publication:20240101",
                "before": f"publication:{date.today():%Y%m%d}",
                "num": 50,
                "language": "ENGLISH",
                "sort": "new",
                "json_restrictor": (
                    "search_metadata,search_information,"
                    "organic_results[].{title,patent_id,patent_link,publication_date,"
                    "filing_date,priority_date,inventor,assignee,publication_number,snippet}"
                ),
            },
            **common,
        ),
    ]


def _news_search(subdomain: str) -> PlannedSearch:
    query = (
        f'"{subdomain}" (startup OR funding OR launch OR partnership OR product) when:1y'
    )
    return PlannedSearch(
        engine="google_news",
        purpose="commercial_events",
        query=query,
        params={"q": query, "hl": "en", "gl": "us"},
        target_subdomains=[subdomain],
    )


def _market_search(subdomain: str) -> PlannedSearch:
    query = f'"{subdomain}" (startup OR company OR product OR platform)'
    return PlannedSearch(
        engine="google",
        purpose="market_presence",
        query=query,
        params={
            "q": query,
            "hl": "en",
            "num": 20,
            "json_restrictor": (
                "search_metadata,search_information,"
                "organic_results[].{position,title,link,source,displayed_link,date,snippet}"
            ),
        },
        target_subdomains=[subdomain],
    )


def _trend_search(subdomains: list[str]) -> PlannedSearch:
    joined = ",".join(subdomains)
    return PlannedSearch(
        engine="google_trends",
        purpose="attention_momentum",
        query=joined,
        params={"q": joined, "data_type": "TIMESERIES", "date": "today 5-y", "hl": "en"},
        target_subdomains=subdomains,
    )


def build_query_plan(technology: str, subdomains: list[str]) -> list[PlannedSearch]:
    del technology  # parent-domain context is reserved for taxonomy/query expansion later

    plan: list[PlannedSearch] = []
    for subdomain in subdomains:
        plan.extend(_scholar_searches(subdomain))
        plan.extend(_patent_searches(subdomain))
        plan.append(_news_search(subdomain))
        plan.append(_market_search(subdomain))

    for start in range(0, len(subdomains), 5):
        plan.append(_trend_search(subdomains[start : start + 5]))

    return plan

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path

from app.schemas.analysis import PlannedSearch
from app.services.serpapi.cache import FileSearchCache, query_fingerprint
from app.services.serpapi.client import SerpApiClient, SerpApiError
from app.services.serpapi.normalizers import EvidenceItem, TrendPoint, normalize_payload


@dataclass(frozen=True)
class SearchRunResult:
    engine: str
    purpose: str
    query: str
    target_subdomains: list[str]
    params: dict[str, str | int | bool]
    status: str
    cached: bool
    fingerprint: str
    result_count: int
    estimated_total_results: int | None
    search_id: str | None
    evidence: list[EvidenceItem]
    trend_points: list[TrendPoint]
    error: str | None = None


async def execute_query_plan(
    *,
    plan: list[PlannedSearch],
    api_key: str,
    cache_dir: Path,
    concurrency: int = 3,
) -> list[SearchRunResult]:
    if concurrency < 1:
        raise ValueError("concurrency must be at least 1")

    cache = FileSearchCache(cache_dir)
    semaphore = asyncio.Semaphore(concurrency)

    async with SerpApiClient(api_key=api_key) as client:
        tasks = [
            _execute_one(search=search, client=client, cache=cache, semaphore=semaphore)
            for search in plan
        ]
        return list(await asyncio.gather(*tasks))


async def _execute_one(
    *,
    search: PlannedSearch,
    client: SerpApiClient,
    cache: FileSearchCache,
    semaphore: asyncio.Semaphore,
) -> SearchRunResult:
    params = dict(search.params)
    fingerprint = query_fingerprint(search.engine, params)
    hit = cache.get(engine=search.engine, params=params)

    if hit is not None:
        return _success_result(search, hit.payload, cached=True, fingerprint=hit.fingerprint)

    try:
        async with semaphore:
            payload = await client.search(engine=search.engine, params=params)
    except SerpApiError as exc:
        return SearchRunResult(
            engine=search.engine,
            purpose=search.purpose,
            query=search.query,
            target_subdomains=search.target_subdomains,
            params=dict(search.params),
            status="error",
            cached=False,
            fingerprint=fingerprint,
            result_count=0,
            estimated_total_results=None,
            search_id=None,
            evidence=[],
            trend_points=[],
            error=str(exc),
        )

    fingerprint = cache.put(engine=search.engine, params=params, payload=payload)
    return _success_result(search, payload, cached=False, fingerprint=fingerprint)


def _success_result(
    search: PlannedSearch,
    payload: dict,
    *,
    cached: bool,
    fingerprint: str,
) -> SearchRunResult:
    normalized = normalize_payload(search.engine, payload)
    return SearchRunResult(
        engine=search.engine,
        purpose=search.purpose,
        query=search.query,
        target_subdomains=search.target_subdomains,
        params=dict(search.params),
        status="success",
        cached=cached,
        fingerprint=fingerprint,
        result_count=normalized.result_count,
        estimated_total_results=normalized.estimated_total_results,
        search_id=normalized.search_id,
        evidence=normalized.evidence,
        trend_points=normalized.trend_points,
    )

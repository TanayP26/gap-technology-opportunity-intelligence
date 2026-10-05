from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.schemas.analysis import (
    AnalysisCreateRequest,
    AnalysisPreviewRequest,
    AnalysisPreviewResponse,
    AnalysisResponse,
    EvidencePreview,
    GapScoreResponse,
    LandscapeResponse,
    LiveProbeRequest,
    LiveProbeResponse,
    SignalVector,
    SourceRunSummary,
)
from app.services.serpapi.queries import build_query_plan
from app.services.serpapi.runner import execute_query_plan
from app.services.signals.derive import derive_signal_vector
from app.services.signals.scoring import score_signal_values
from app.storage.postgres import (
    DatabaseUnavailable,
    create_analysis_record,
    get_analysis,
    get_landscape,
    mark_analysis_failed,
    persist_analysis_results,
)

router = APIRouter(prefix="/api/v1/analyses", tags=["analyses"])


@router.post("/preview", response_model=AnalysisPreviewResponse)
def preview_analysis(payload: AnalysisPreviewRequest) -> AnalysisPreviewResponse:
    plan = build_query_plan(payload.technology, payload.subdomains)
    return AnalysisPreviewResponse(
        technology=payload.technology,
        subdomains=payload.subdomains,
        planned_searches=plan,
        estimated_serpapi_calls=len(plan),
    )


@router.post("/score", response_model=GapScoreResponse)
def score_signals(signals: SignalVector) -> GapScoreResponse:
    return GapScoreResponse(signals=signals, **score_signal_values(**signals.model_dump()))


@router.post("/probe", response_model=LiveProbeResponse)
async def probe_subdomain(payload: LiveProbeRequest) -> LiveProbeResponse:
    _require_live_search(payload.confirm_live_search)
    settings = get_settings()
    _require_serpapi(settings.serpapi_api_key)

    plan = build_query_plan(payload.technology, [payload.subdomain])
    runs = await execute_query_plan(
        plan=plan,
        api_key=settings.serpapi_api_key,
        cache_dir=Path(settings.search_cache_dir),
        concurrency=settings.serpapi_concurrency,
    )

    signals = derive_signal_vector(runs, payload.subdomain)
    score = GapScoreResponse(signals=signals, **score_signal_values(**signals.model_dump()))
    evidence = [item for run in runs for item in run.evidence]
    trend_points = [point for run in runs for point in run.trend_points]

    source_runs = [
        SourceRunSummary(
            engine=run.engine,
            purpose=run.purpose,
            status=run.status,
            cached=run.cached,
            result_count=run.result_count,
            estimated_total_results=run.estimated_total_results,
            search_id=run.search_id,
            error=run.error,
        )
        for run in runs
    ]
    evidence_preview = [
        EvidencePreview(
            evidence_type=item.evidence_type,
            title=item.title,
            url=item.url,
            source_name=item.source_name,
            published_at=item.published_at,
            snippet=item.snippet,
        )
        for item in evidence[:20]
    ]

    return LiveProbeResponse(
        technology=payload.technology,
        subdomain=payload.subdomain,
        source_runs=source_runs,
        signals=signals,
        score=score,
        evidence_count=len(evidence),
        trend_point_count=len(trend_points),
        evidence_preview=evidence_preview,
    )


@router.post("", response_model=AnalysisResponse)
async def create_analysis(payload: AnalysisCreateRequest) -> AnalysisResponse:
    _require_live_search(payload.confirm_live_search)
    settings = get_settings()
    _require_serpapi(settings.serpapi_api_key)

    try:
        analysis_id, subdomain_ids = await create_analysis_record(
            database_url=settings.database_url,
            technology=payload.technology,
            geography=payload.geography,
            subdomains=payload.subdomains,
        )
    except DatabaseUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="PostgreSQL is unavailable or the GAP schema has not been migrated.",
        ) from exc

    try:
        plan = build_query_plan(payload.technology, payload.subdomains)
        runs = await execute_query_plan(
            plan=plan,
            api_key=settings.serpapi_api_key,
            cache_dir=Path(settings.search_cache_dir),
            concurrency=settings.serpapi_concurrency,
        )

        scores: dict[str, GapScoreResponse] = {}
        for subdomain in payload.subdomains:
            signals = derive_signal_vector(runs, subdomain)
            scores[subdomain] = GapScoreResponse(
                signals=signals,
                **score_signal_values(**signals.model_dump()),
            )

        await persist_analysis_results(
            database_url=settings.database_url,
            analysis_id=analysis_id,
            subdomain_ids=subdomain_ids,
            runs=runs,
            scores=scores,
        )
    except Exception as exc:
        try:
            await mark_analysis_failed(
                database_url=settings.database_url,
                analysis_id=analysis_id,
                reason=str(exc),
            )
        finally:
            raise HTTPException(status_code=502, detail="Analysis execution failed.") from exc

    result = await get_analysis(settings.database_url, analysis_id)
    if result is None:
        raise HTTPException(status_code=500, detail="Analysis completed but could not be reloaded.")
    return result


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def read_analysis(analysis_id: UUID) -> AnalysisResponse:
    settings = get_settings()
    try:
        result = await get_analysis(settings.database_url, analysis_id)
    except DatabaseUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail="PostgreSQL is unavailable.") from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result


@router.get("/{analysis_id}/landscape", response_model=LandscapeResponse)
async def read_landscape(analysis_id: UUID) -> LandscapeResponse:
    settings = get_settings()
    try:
        result = await get_landscape(settings.database_url, analysis_id)
    except DatabaseUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail="PostgreSQL is unavailable.") from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result


def _require_live_search(confirmed: bool) -> None:
    if not confirmed:
        raise HTTPException(
            status_code=400,
            detail="Set confirm_live_search=true to execute SerpApi searches.",
        )


def _require_serpapi(api_key: str) -> None:
    if not api_key:
        raise HTTPException(status_code=503, detail="SERPAPI_API_KEY is not configured")

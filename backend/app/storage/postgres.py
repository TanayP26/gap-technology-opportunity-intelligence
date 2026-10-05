from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.schemas.analysis import (
    AnalysisResponse,
    EvidenceItemResponse,
    EvidenceListResponse,
    GapScoreResponse,
    LandscapeEntry,
    LandscapeResponse,
    SignalVector,
    SubdomainAnalysis,
)
from app.services.serpapi.runner import SearchRunResult

FORMULA_VERSION = "gap-v1.1"


class DatabaseUnavailable(RuntimeError):
    pass


def _driver():
    try:
        from psycopg import AsyncConnection
        from psycopg.rows import dict_row
        from psycopg.types.json import Jsonb
    except ModuleNotFoundError as exc:
        raise DatabaseUnavailable(
            'PostgreSQL driver is not installed. Run: pip install -e ".[dev]"'
        ) from exc
    return AsyncConnection, dict_row, Jsonb


async def database_ready(database_url: str) -> bool:
    AsyncConnection, _, _ = _driver()
    try:
        conn = await AsyncConnection.connect(database_url, connect_timeout=3)
        async with conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False


async def create_analysis_record(
    *, database_url: str,
    technology: str,
    geography: str,
    subdomains: list[str],
) -> tuple[UUID, dict[str, UUID]]:
    AsyncConnection, dict_row, _ = _driver()
    conn = await AsyncConnection.connect(database_url, row_factory=dict_row, connect_timeout=5)

    async with conn:
        async with conn.transaction():
            cursor = await conn.execute(
                """
                INSERT INTO analyses (technology, geography, status, started_at)
                VALUES (%s, %s, 'running', now())
                RETURNING id
                """,
                (technology, geography),
            )
            analysis_row = await cursor.fetchone()
            analysis_id = analysis_row["id"]

            ids: dict[str, UUID] = {}
            used_slugs: set[str] = set()
            for position, name in enumerate(subdomains, start=1):
                slug = _unique_slug(name, used_slugs)
                cursor = await conn.execute(
                    """
                    INSERT INTO subdomains (analysis_id, name, slug, position)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (analysis_id, name, slug, position),
                )
                row = await cursor.fetchone()
                ids[name.casefold()] = row["id"]

    return analysis_id, ids


async def persist_analysis_results(
    *,
    database_url: str,
    analysis_id: UUID,
    subdomain_ids: dict[str, UUID],
    runs: list[SearchRunResult],
    scores: dict[str, GapScoreResponse],
) -> None:
    AsyncConnection, _, Jsonb = _driver()
    conn = await AsyncConnection.connect(database_url, connect_timeout=5)

    async with conn:
        async with conn.transaction():
            for run in runs:
                run_ids: dict[str, UUID] = {}
                for target in run.target_subdomains:
                    subdomain_id = subdomain_ids.get(target.casefold())
                    if subdomain_id is None:
                        continue
                    cursor = await conn.execute(
                        """
                        INSERT INTO search_runs (
                            analysis_id, subdomain_id, engine, purpose, query, params,
                            query_fingerprint, status, serpapi_search_id, result_count,
                            error_message, completed_at
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now()
                        )
                        RETURNING id
                        """,
                        (
                            analysis_id,
                            subdomain_id,
                            run.engine,
                            run.purpose,
                            run.query,
                            Jsonb(run.params),
                            run.fingerprint,
                            _stored_run_status(run),
                            run.search_id,
                            run.result_count,
                            run.error,
                        ),
                    )
                    row = await cursor.fetchone()
                    run_ids[target.casefold()] = row[0] if not isinstance(row, dict) else row["id"]

                if len(run.target_subdomains) == 1:
                    target = run.target_subdomains[0]
                    subdomain_id = subdomain_ids.get(target.casefold())
                    search_run_id = run_ids.get(target.casefold())
                    if subdomain_id is not None and search_run_id is not None:
                        for item in run.evidence:
                            metadata = dict(item.metadata)
                            published_at = _parse_datetime(item.published_at)
                            if item.published_at and published_at is None:
                                metadata["raw_published_at"] = item.published_at
                            await conn.execute(
                                """
                                INSERT INTO evidence_items (
                                    analysis_id, subdomain_id, search_run_id, evidence_type,
                                    title, url, source_name, published_at, snippet,
                                    external_id, metadata
                                )
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (
                                    analysis_id,
                                    subdomain_id,
                                    search_run_id,
                                    item.evidence_type,
                                    item.title,
                                    item.url,
                                    item.source_name,
                                    published_at,
                                    item.snippet,
                                    item.external_id,
                                    Jsonb(metadata),
                                ),
                            )

                for point in run.trend_points:
                    subdomain_id = subdomain_ids.get(point.query.casefold())
                    observed_at = _trend_datetime(point.timestamp, point.date)
                    if subdomain_id is None or observed_at is None:
                        continue
                    await conn.execute(
                        """
                        INSERT INTO trend_points (analysis_id, subdomain_id, observed_at, value)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (subdomain_id, observed_at)
                        DO UPDATE SET value = EXCLUDED.value
                        """,
                        (analysis_id, subdomain_id, observed_at, point.value),
                    )

            for subdomain_name, score in scores.items():
                subdomain_id = subdomain_ids[subdomain_name.casefold()]
                signals = score.signals
                await conn.execute(
                    """
                    INSERT INTO signal_snapshots (
                        analysis_id, subdomain_id, research, patents, attention, events,
                        market, confidence, technical_momentum, demand_momentum,
                        whitespace, gap_score, formula_version, score_status, missing_signals
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        analysis_id,
                        subdomain_id,
                        signals.research,
                        signals.patents,
                        signals.attention,
                        signals.events,
                        signals.market,
                        signals.confidence,
                        score.technical_momentum,
                        score.demand_momentum,
                        score.whitespace,
                        score.gap_score,
                        FORMULA_VERSION,
                        score.status,
                        Jsonb(score.missing_signals),
                    ),
                )

            await conn.execute(
                """
                UPDATE analyses
                SET status = 'complete', completed_at = now(), failure_reason = NULL
                WHERE id = %s
                """,
                (analysis_id,),
            )


async def mark_analysis_failed(
    *, database_url: str, analysis_id: UUID, reason: str
) -> None:
    AsyncConnection, _, _ = _driver()
    conn = await AsyncConnection.connect(database_url, connect_timeout=5)
    async with conn:
        await conn.execute(
            """
            UPDATE analyses
            SET status = 'failed', completed_at = now(), failure_reason = %s
            WHERE id = %s
            """,
            (reason[:1000], analysis_id),
        )


async def get_analysis(database_url: str, analysis_id: UUID) -> AnalysisResponse | None:
    AsyncConnection, dict_row, _ = _driver()
    conn = await AsyncConnection.connect(database_url, row_factory=dict_row, connect_timeout=5)
    async with conn:
        cursor = await conn.execute("SELECT * FROM analyses WHERE id = %s", (analysis_id,))
        analysis = await cursor.fetchone()
        if analysis is None:
            return None

        cursor = await conn.execute(
            """
            SELECT
                s.id,
                s.name,
                s.position,
                ss.research,
                ss.patents,
                ss.attention,
                ss.events,
                ss.market,
                ss.confidence,
                ss.technical_momentum,
                ss.demand_momentum,
                ss.whitespace,
                ss.gap_score,
                ss.score_status,
                ss.missing_signals,
                ss.id AS signal_snapshot_id,
                COALESCE(e.evidence_count, 0) AS evidence_count,
                COALESCE(r.source_error_count, 0) AS source_error_count
            FROM subdomains s
            LEFT JOIN LATERAL (
                SELECT *
                FROM signal_snapshots x
                WHERE x.subdomain_id = s.id
                ORDER BY x.created_at DESC
                LIMIT 1
            ) ss ON true
            LEFT JOIN LATERAL (
                SELECT count(*)::int AS evidence_count
                FROM evidence_items x
                WHERE x.subdomain_id = s.id
            ) e ON true
            LEFT JOIN LATERAL (
                SELECT count(*)::int AS source_error_count
                FROM search_runs x
                WHERE x.subdomain_id = s.id AND x.status = 'error'
            ) r ON true
            WHERE s.analysis_id = %s
            ORDER BY s.position
            """,
            (analysis_id,),
        )
        rows = await cursor.fetchall()

    subdomains = [_subdomain_model(row) for row in rows if row["signal_snapshot_id"] is not None]
    return AnalysisResponse(
        id=analysis["id"],
        technology=analysis["technology"],
        geography=analysis["geography"],
        status=analysis["status"],
        created_at=_iso(analysis["created_at"]),
        started_at=_iso_optional(analysis["started_at"]),
        completed_at=_iso_optional(analysis["completed_at"]),
        failure_reason=analysis["failure_reason"],
        subdomains=subdomains,
    )


async def get_landscape(database_url: str, analysis_id: UUID) -> LandscapeResponse | None:
    analysis = await get_analysis(database_url, analysis_id)
    if analysis is None:
        return None

    entries = [
        LandscapeEntry(
            subdomain_id=item.id,
            name=item.name,
            position=item.position,
            signals=item.signals,
            score_status=item.score.status,
            missing_signals=item.score.missing_signals,
            technical_momentum=item.score.technical_momentum,
            demand_momentum=item.score.demand_momentum,
            whitespace=item.score.whitespace,
            gap_score=item.score.gap_score,
            evidence_count=item.evidence_count,
            source_error_count=item.source_error_count,
        )
        for item in analysis.subdomains
    ]
    entries.sort(
        key=lambda item: (
            item.gap_score is None,
            -(item.gap_score or 0.0),
            item.position,
        )
    )
    return LandscapeResponse(
        analysis_id=analysis.id,
        technology=analysis.technology,
        status=analysis.status,
        entries=entries,
    )


async def get_subdomain_evidence(
    *,
    database_url: str,
    subdomain_id: UUID,
    evidence_type: str | None,
    limit: int,
    offset: int,
) -> EvidenceListResponse | None:
    AsyncConnection, dict_row, _ = _driver()
    conn = await AsyncConnection.connect(database_url, row_factory=dict_row, connect_timeout=5)
    async with conn:
        cursor = await conn.execute("SELECT id FROM subdomains WHERE id = %s", (subdomain_id,))
        if await cursor.fetchone() is None:
            return None

        where = "subdomain_id = %s"
        params: list[Any] = [subdomain_id]
        if evidence_type:
            where += " AND evidence_type = %s"
            params.append(evidence_type)

        cursor = await conn.execute(
            f"SELECT count(*)::int AS total FROM evidence_items WHERE {where}",
            tuple(params),
        )
        total = (await cursor.fetchone())["total"]

        cursor = await conn.execute(
            f"""
            SELECT id, evidence_type, title, url, source_name, published_at,
                   snippet, external_id, metadata
            FROM evidence_items
            WHERE {where}
            ORDER BY published_at DESC NULLS LAST, created_at DESC
            LIMIT %s OFFSET %s
            """,
            tuple([*params, limit, offset]),
        )
        rows = await cursor.fetchall()

    return EvidenceListResponse(
        subdomain_id=subdomain_id,
        total=total,
        limit=limit,
        offset=offset,
        items=[
            EvidenceItemResponse(
                id=row["id"],
                evidence_type=row["evidence_type"],
                title=row["title"],
                url=row["url"],
                source_name=row["source_name"],
                published_at=_iso_optional(row["published_at"]),
                snippet=row["snippet"],
                external_id=row["external_id"],
                metadata=row["metadata"] or {},
            )
            for row in rows
        ],
    )


def _subdomain_model(row: dict[str, Any]) -> SubdomainAnalysis:
    signals = SignalVector(
        research=_float_optional(row["research"]),
        patents=_float_optional(row["patents"]),
        attention=_float_optional(row["attention"]),
        events=_float_optional(row["events"]),
        market=_float_optional(row["market"]),
        confidence=float(row["confidence"]),
    )
    score = GapScoreResponse(
        signals=signals,
        status=row.get("score_status") or "scored",
        missing_signals=row.get("missing_signals") or [],
        technical_momentum=_float_optional(row["technical_momentum"]),
        demand_momentum=_float_optional(row["demand_momentum"]),
        whitespace=_float_optional(row["whitespace"]),
        gap_score=_float_optional(row["gap_score"]),
    )
    return SubdomainAnalysis(
        id=row["id"],
        name=row["name"],
        position=row["position"],
        signals=signals,
        score=score,
        evidence_count=row["evidence_count"],
        source_error_count=row["source_error_count"],
    )


def _float_optional(value: Any) -> float | None:
    return float(value) if value is not None else None


def _stored_run_status(run: SearchRunResult) -> str:
    if run.status == "error":
        return "error"
    return "cached" if run.cached else "success"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug or "subdomain"


def _unique_slug(value: str, used: set[str]) -> str:
    base = _slugify(value)
    slug = base
    suffix = 2
    while slug in used:
        slug = f"{base}-{suffix}"
        suffix += 1
    used.add(slug)
    return slug


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    candidates = [text, text.replace("Z", "+00:00")]
    for candidate in candidates:
        try:
            parsed = datetime.fromisoformat(candidate)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=UTC)
            return parsed
        except ValueError:
            pass
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%b %d, %Y", "%Y"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=UTC)
        except ValueError:
            pass
    return None


def _trend_datetime(timestamp: str | None, date_text: str) -> datetime | None:
    if timestamp:
        try:
            return datetime.fromtimestamp(float(timestamp), tz=UTC)
        except (TypeError, ValueError, OSError):
            pass
    return _parse_datetime(date_text)


def _iso(value: datetime) -> str:
    return value.isoformat()


def _iso_optional(value: datetime | None) -> str | None:
    return value.isoformat() if value else None

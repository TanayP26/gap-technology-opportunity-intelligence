from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from app.schemas.analysis import EngineName

EvidenceType = Literal["paper", "patent", "news", "market"]


@dataclass(frozen=True)
class EvidenceItem:
    evidence_type: EvidenceType
    title: str
    url: str | None = None
    source_name: str | None = None
    published_at: str | None = None
    snippet: str | None = None
    external_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TrendPoint:
    query: str
    date: str
    value: float
    timestamp: str | None = None


@dataclass(frozen=True)
class NormalizedPayload:
    engine: EngineName
    evidence: list[EvidenceItem]
    trend_points: list[TrendPoint]
    result_count: int
    estimated_total_results: int | None
    search_id: str | None


def normalize_payload(engine: EngineName, payload: dict[str, Any]) -> NormalizedPayload:
    if engine == "google_scholar":
        return _normalize_scholar(payload)
    if engine == "google_patents":
        return _normalize_patents(payload)
    if engine == "google_news":
        return _normalize_news(payload)
    if engine == "google":
        return _normalize_google(payload)
    if engine == "google_trends":
        return _normalize_trends(payload)
    raise ValueError(f"Unsupported engine: {engine}")


def _metadata(payload: dict[str, Any]) -> tuple[str | None, int | None]:
    metadata = payload.get("search_metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    information = payload.get("search_information")
    if not isinstance(information, dict):
        information = {}
    search_id = _string(metadata.get("id"))
    return search_id, _integer(information.get("total_results"))


def _normalize_scholar(payload: dict[str, Any]) -> NormalizedPayload:
    search_id, total = _metadata(payload)
    evidence: list[EvidenceItem] = []
    for result in _list_of_dicts(payload.get("organic_results")):
        publication = result.get("publication_info") or {}
        inline_links = result.get("inline_links") or {}
        cited_by = inline_links.get("cited_by") or result.get("cited_by") or {}
        authors = [
            author.get("name")
            for author in _list_of_dicts(publication.get("authors"))
            if author.get("name")
        ]
        evidence.append(
            EvidenceItem(
                evidence_type="paper",
                title=_string(result.get("title")) or "Untitled paper",
                url=_string(result.get("link")),
                source_name=_string(publication.get("summary")),
                snippet=_string(result.get("snippet")),
                external_id=_string(result.get("result_id")),
                metadata={
                    "authors": authors,
                    "citation_count": _integer(cited_by.get("total")),
                    "cites_id": _string(cited_by.get("cites_id")),
                },
            )
        )
    return NormalizedPayload(
        engine="google_scholar",
        evidence=evidence,
        trend_points=[],
        result_count=len(evidence),
        estimated_total_results=total,
        search_id=search_id,
    )


def _normalize_patents(payload: dict[str, Any]) -> NormalizedPayload:
    search_id, total = _metadata(payload)
    evidence: list[EvidenceItem] = []
    for result in _list_of_dicts(payload.get("organic_results")):
        evidence.append(
            EvidenceItem(
                evidence_type="patent",
                title=_string(result.get("title")) or "Untitled patent",
                url=_string(result.get("patent_link")) or _string(result.get("link")),
                source_name=_participant_name(result.get("assignee")),
                published_at=_string(result.get("publication_date")),
                snippet=_string(result.get("snippet")),
                external_id=(
                    _string(result.get("patent_id"))
                    or _string(result.get("publication_number"))
                ),
                metadata={
                    "filing_date": _string(result.get("filing_date")),
                    "priority_date": _string(result.get("priority_date")),
                    "inventor": result.get("inventor"),
                    "assignee": result.get("assignee"),
                },
            )
        )
    return NormalizedPayload(
        engine="google_patents",
        evidence=evidence,
        trend_points=[],
        result_count=len(evidence),
        estimated_total_results=total,
        search_id=search_id,
    )


def _normalize_news(payload: dict[str, Any]) -> NormalizedPayload:
    search_id, total = _metadata(payload)
    evidence: list[EvidenceItem] = []
    for result in _list_of_dicts(payload.get("news_results")):
        source = result.get("source")
        if isinstance(source, dict):
            source_name = _string(source.get("name"))
        else:
            source_name = _string(source)
        evidence.append(
            EvidenceItem(
                evidence_type="news",
                title=_string(result.get("title")) or "Untitled news item",
                url=_string(result.get("link")),
                source_name=source_name,
                published_at=(
                    _string(result.get("iso_date"))
                    or _string(result.get("published_at"))
                    or _string(result.get("date"))
                ),
                snippet=_string(result.get("snippet")),
                external_id=_string(result.get("story_token")),
                metadata={"position": _integer(result.get("position"))},
            )
        )
    return NormalizedPayload(
        engine="google_news",
        evidence=evidence,
        trend_points=[],
        result_count=len(evidence),
        estimated_total_results=total,
        search_id=search_id,
    )


def _normalize_google(payload: dict[str, Any]) -> NormalizedPayload:
    search_id, total = _metadata(payload)
    evidence: list[EvidenceItem] = []
    for result in _list_of_dicts(payload.get("organic_results")):
        evidence.append(
            EvidenceItem(
                evidence_type="market",
                title=_string(result.get("title")) or "Untitled result",
                url=_string(result.get("link")),
                source_name=_string(result.get("source")) or _string(result.get("displayed_link")),
                published_at=_string(result.get("date")),
                snippet=_string(result.get("snippet")),
                metadata={"position": _integer(result.get("position"))},
            )
        )
    return NormalizedPayload(
        engine="google",
        evidence=evidence,
        trend_points=[],
        result_count=len(evidence),
        estimated_total_results=total,
        search_id=search_id,
    )


def _normalize_trends(payload: dict[str, Any]) -> NormalizedPayload:
    search_id, _ = _metadata(payload)
    points: list[TrendPoint] = []
    interest = payload.get("interest_over_time")
    if not isinstance(interest, dict):
        interest = {}
    timeline = interest.get("timeline_data")
    for row in _list_of_dicts(timeline):
        row_date = _string(row.get("date")) or ""
        row_timestamp = _string(row.get("timestamp"))
        for value in _list_of_dicts(row.get("values")):
            query = _string(value.get("query"))
            if not query:
                continue
            extracted = value.get("extracted_value", value.get("value"))
            numeric = _float(extracted)
            if numeric is None:
                continue
            points.append(
                TrendPoint(
                    query=query,
                    date=row_date,
                    value=numeric,
                    timestamp=_string(value.get("timestamp")) or row_timestamp,
                )
            )
    return NormalizedPayload(
        engine="google_trends",
        evidence=[],
        trend_points=points,
        result_count=len(points),
        estimated_total_results=None,
        search_id=search_id,
    )


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _integer(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def _float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str):
        value = value.replace("<", "").replace("%", "").strip()
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _participant_name(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, list):
        names = []
        for item in value:
            if isinstance(item, dict):
                name = _string(item.get("name"))
            else:
                name = _string(item)
            if name:
                names.append(name)
        return ", ".join(names) or None
    if isinstance(value, dict):
        return _string(value.get("name"))
    return None

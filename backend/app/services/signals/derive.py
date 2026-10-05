from __future__ import annotations

from datetime import UTC, date, datetime

from app.schemas.analysis import SignalVector
from app.services.serpapi.runner import SearchRunResult
from app.services.signals.scoring import (
    confidence_score,
    momentum_from_windows,
    presence_score,
    trend_momentum,
)

BASELINE_YEARS = 2.0
RECENT_WINDOW_START = date(2024, 1, 1)
REQUIRED_PURPOSES = {
    "research_baseline",
    "research_recent",
    "patent_baseline",
    "patent_recent",
    "commercial_events",
    "market_presence",
    "attention_momentum",
}


def derive_signal_vector(runs: list[SearchRunResult], subdomain: str) -> SignalVector:
    target = subdomain.casefold()
    targeted = [
        run
        for run in runs
        if any(name.casefold() == target for name in run.target_subdomains)
    ]
    successful = [run for run in targeted if run.status == "success"]
    successful_purposes = {run.purpose for run in successful}

    recent_years = max(
        (datetime.now(UTC).date() - RECENT_WINDOW_START).days / 365.25,
        0.25,
    )

    research = None
    if {"research_baseline", "research_recent"} <= successful_purposes:
        research = momentum_from_windows(
            recent_count=_total_for(successful, "research_recent"),
            recent_years=recent_years,
            baseline_count=_total_for(successful, "research_baseline"),
            baseline_years=BASELINE_YEARS,
        )

    patents = None
    if {"patent_baseline", "patent_recent"} <= successful_purposes:
        patents = momentum_from_windows(
            recent_count=_total_for(successful, "patent_recent"),
            recent_years=recent_years,
            baseline_count=_total_for(successful, "patent_baseline"),
            baseline_years=BASELINE_YEARS,
        )

    attention = None
    if "attention_momentum" in successful_purposes:
        attention = trend_momentum(_trend_values(successful, subdomain))

    events = None
    if "commercial_events" in successful_purposes:
        events = presence_score(
            _result_count_for(successful, "commercial_events"),
            saturation=10.0,
        )

    market = None
    if "market_presence" in successful_purposes:
        market = presence_score(
            _result_count_for(successful, "market_presence"),
            saturation=12.0,
        )

    trend_values = _trend_values(successful, subdomain)
    base_confidence = confidence_score(
        scholar_count=_evidence_count(successful, "paper"),
        patent_count=_evidence_count(successful, "patent"),
        news_count=_evidence_count(successful, "news"),
        market_count=_evidence_count(successful, "market"),
        trend_points=len(trend_values),
    )
    source_coverage = len(successful_purposes & REQUIRED_PURPOSES) / len(REQUIRED_PURPOSES)
    confidence = base_confidence * source_coverage

    return SignalVector(
        research=research,
        patents=patents,
        attention=attention,
        events=events,
        market=market,
        confidence=confidence,
    )


def _total_for(runs: list[SearchRunResult], purpose: str) -> int:
    matching = [run for run in runs if run.purpose == purpose]
    if not matching:
        return 0
    return sum(
        run.estimated_total_results
        if run.estimated_total_results is not None
        else run.result_count
        for run in matching
    )


def _result_count_for(runs: list[SearchRunResult], purpose: str) -> int:
    return sum(run.result_count for run in runs if run.purpose == purpose)


def _evidence_count(runs: list[SearchRunResult], evidence_type: str) -> int:
    return sum(
        1
        for run in runs
        for item in run.evidence
        if item.evidence_type == evidence_type
    )


def _trend_values(runs: list[SearchRunResult], subdomain: str) -> list[float]:
    target = subdomain.casefold()
    points = [
        point
        for run in runs
        for point in run.trend_points
        if point.query.casefold() == target
    ]
    return [point.value for point in points]

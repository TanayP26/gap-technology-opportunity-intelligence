from __future__ import annotations

import math
from collections.abc import Iterable


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def momentum_from_windows(
    recent_count: int,
    recent_years: float,
    baseline_count: int,
    baseline_years: float,
) -> float:
    if recent_years <= 0 or baseline_years <= 0:
        raise ValueError("window lengths must be positive")

    recent_rate = recent_count / recent_years
    baseline_rate = baseline_count / baseline_years

    if recent_rate == 0 and baseline_rate == 0:
        return 0.0

    relative_change = (recent_rate - baseline_rate) / (baseline_rate + 1.0)
    return clamp01(0.5 + 0.5 * math.tanh(relative_change / 2.0))


def presence_score(result_count: int, saturation: float = 20.0) -> float:
    if result_count <= 0:
        return 0.0
    if saturation <= 0:
        raise ValueError("saturation must be positive")
    return clamp01(1.0 - math.exp(-result_count / saturation))


def trend_momentum(values: Iterable[float]) -> float:
    series = [max(0.0, float(value)) for value in values]
    if len(series) < 6:
        return 0.0

    window = max(2, len(series) // 3)
    early = sum(series[:window]) / window
    recent = sum(series[-window:]) / window

    if early == 0 and recent == 0:
        return 0.0

    relative_change = (recent - early) / (early + 1.0)
    return clamp01(0.5 + 0.5 * math.tanh(relative_change / 2.0))


def confidence_score(
    *,
    scholar_count: int,
    patent_count: int,
    news_count: int,
    market_count: int,
    trend_points: int,
) -> float:
    saturations = {
        "scholar": (scholar_count, 20),
        "patent": (patent_count, 30),
        "news": (news_count, 12),
        "market": (market_count, 12),
        "trends": (trend_points, 36),
    }

    evidence_strength = sum(
        min(count / saturation, 1.0) for count, saturation in saturations.values()
    ) / len(saturations)
    source_coverage = sum(count > 0 for count, _ in saturations.values()) / len(saturations)

    return clamp01(0.7 * evidence_strength + 0.3 * source_coverage)


def gap_score(
    *,
    research: float,
    patents: float,
    attention: float,
    events: float,
    market: float,
    confidence: float,
) -> dict[str, float]:
    values = [research, patents, attention, events, market, confidence]
    if any(value < 0 or value > 1 for value in values):
        raise ValueError("all signals must be between 0 and 1")

    technical = 0.55 * research + 0.45 * patents
    demand = 0.55 * attention + 0.45 * events
    whitespace = technical * demand * (1.0 - market)
    score = whitespace * confidence

    return {
        "technical_momentum": round(technical, 4),
        "demand_momentum": round(demand, 4),
        "whitespace": round(whitespace, 4),
        "gap_score": round(score, 4),
    }


SIGNAL_NAMES = ("research", "patents", "attention", "events", "market")


def score_signal_values(
    *,
    research: float | None,
    patents: float | None,
    attention: float | None,
    events: float | None,
    market: float | None,
    confidence: float,
) -> dict[str, float | str | list[str] | None]:
    values = {
        "research": research,
        "patents": patents,
        "attention": attention,
        "events": events,
        "market": market,
    }
    missing = [name for name in SIGNAL_NAMES if values[name] is None]
    if missing:
        return {
            "status": "insufficient_evidence",
            "missing_signals": missing,
            "technical_momentum": None,
            "demand_momentum": None,
            "whitespace": None,
            "gap_score": None,
        }

    score = gap_score(
        research=float(research),
        patents=float(patents),
        attention=float(attention),
        events=float(events),
        market=float(market),
        confidence=confidence,
    )
    return {
        "status": "scored",
        "missing_signals": [],
        **score,
    }

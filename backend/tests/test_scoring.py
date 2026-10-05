import pytest

from app.services.signals.scoring import (
    confidence_score,
    gap_score,
    momentum_from_windows,
    presence_score,
    score_signal_values,
    trend_momentum,
)


def test_growth_scores_above_neutral() -> None:
    score = momentum_from_windows(
        recent_count=40,
        recent_years=2,
        baseline_count=20,
        baseline_years=2,
    )
    assert score > 0.5


def test_decline_scores_below_neutral() -> None:
    score = momentum_from_windows(
        recent_count=8,
        recent_years=2,
        baseline_count=30,
        baseline_years=2,
    )
    assert 0 < score < 0.5


def test_empty_windows_are_not_fake_neutral() -> None:
    assert momentum_from_windows(0, 2, 0, 2) == 0.0


def test_market_presence_saturates_without_exceeding_one() -> None:
    assert presence_score(0) == 0.0
    assert 0 < presence_score(10) < presence_score(100) <= 1.0


def test_trend_momentum_detects_rising_series() -> None:
    score = trend_momentum([5, 6, 7, 8, 15, 20, 25, 30, 36])
    assert score > 0.5


def test_confidence_rewards_cross_source_coverage() -> None:
    sparse = confidence_score(
        scholar_count=20,
        patent_count=0,
        news_count=0,
        market_count=0,
        trend_points=0,
    )
    broad = confidence_score(
        scholar_count=20,
        patent_count=20,
        news_count=10,
        market_count=10,
        trend_points=30,
    )
    assert broad > sparse


def test_gap_score_penalizes_mature_market() -> None:
    early = gap_score(
        research=0.9,
        patents=0.8,
        attention=0.8,
        events=0.7,
        market=0.2,
        confidence=0.9,
    )
    mature = gap_score(
        research=0.9,
        patents=0.8,
        attention=0.8,
        events=0.7,
        market=0.9,
        confidence=0.9,
    )
    assert early["gap_score"] > mature["gap_score"]


def test_signal_bounds_are_enforced() -> None:
    with pytest.raises(ValueError):
        gap_score(
            research=1.2,
            patents=0.5,
            attention=0.5,
            events=0.5,
            market=0.5,
            confidence=0.5,
        )


def test_missing_market_signal_blocks_gap_score() -> None:
    result = score_signal_values(
        research=0.7,
        patents=0.6,
        attention=0.8,
        events=0.5,
        market=None,
        confidence=0.7,
    )

    assert result["status"] == "insufficient_evidence"
    assert result["missing_signals"] == ["market"]
    assert result["gap_score"] is None


def test_complete_signal_vector_still_scores_normally() -> None:
    result = score_signal_values(
        research=0.7,
        patents=0.6,
        attention=0.8,
        events=0.5,
        market=0.2,
        confidence=0.9,
    )

    assert result["status"] == "scored"
    assert result["missing_signals"] == []
    assert result["gap_score"] is not None

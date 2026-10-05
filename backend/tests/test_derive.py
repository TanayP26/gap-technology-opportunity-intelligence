from app.services.serpapi.normalizers import EvidenceItem, TrendPoint
from app.services.serpapi.runner import SearchRunResult
from app.services.signals.derive import derive_signal_vector


def run(
    purpose: str,
    *,
    target: str = "Event-Based Vision",
    total: int | None = None,
    result_count: int = 0,
    evidence_type: str | None = None,
    trend_values: list[float] | None = None,
    status: str = "success",
    error: str | None = None,
) -> SearchRunResult:
    evidence = []
    if evidence_type:
        evidence = [
            EvidenceItem(evidence_type=evidence_type, title="item")
            for _ in range(result_count)
        ]
    points = [
        TrendPoint(query=target, date=str(index), value=value)
        for index, value in enumerate(trend_values or [])
    ]
    return SearchRunResult(
        engine="google",
        purpose=purpose,
        query=target,
        target_subdomains=[target],
        params={"q": target},
        status=status,
        cached=False,
        fingerprint="abc",
        result_count=result_count if not points else len(points),
        estimated_total_results=total,
        search_id="search-id",
        evidence=evidence,
        trend_points=points,
        error=error,
    )


def test_derive_builds_cross_source_vector() -> None:
    runs = [
        run("research_baseline", total=100, result_count=10, evidence_type="paper"),
        run("research_recent", total=260, result_count=10, evidence_type="paper"),
        run("patent_baseline", total=50, result_count=10, evidence_type="patent"),
        run("patent_recent", total=170, result_count=10, evidence_type="patent"),
        run("commercial_events", result_count=8, evidence_type="news"),
        run("market_presence", result_count=3, evidence_type="market"),
        run("attention_momentum", trend_values=[5, 6, 8, 12, 20, 30, 40]),
    ]

    signals = derive_signal_vector(runs, "Event-Based Vision")

    assert signals.research > 0.5
    assert signals.patents > 0.5
    assert signals.attention > 0.5
    assert 0 < signals.market < 1
    assert signals.confidence > 0.5


def test_derive_does_not_mix_other_subdomains() -> None:
    runs = [
        run("research_baseline", total=100, target="Event-Based Vision"),
        run("research_recent", total=200, target="Event-Based Vision"),
        run("research_baseline", total=5, target="Memristive Computing"),
        run("research_recent", total=50000, target="Memristive Computing"),
    ]

    event_signal = derive_signal_vector(runs, "Event-Based Vision")
    memristive_signal = derive_signal_vector(runs, "Memristive Computing")

    assert event_signal.research != memristive_signal.research


def test_failed_market_source_is_unknown_not_zero() -> None:
    runs = [
        run("research_baseline", total=100),
        run("research_recent", total=200),
        run("patent_baseline", total=50),
        run("patent_recent", total=80),
        run("commercial_events", result_count=4, evidence_type="news"),
        run(
            "market_presence",
            status="error",
            error="temporary upstream failure",
        ),
        run("attention_momentum", trend_values=[5, 6, 8, 10]),
    ]

    signals = derive_signal_vector(runs, "Event-Based Vision")

    assert signals.market is None
    assert signals.confidence < 1

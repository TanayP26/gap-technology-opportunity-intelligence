import json
from pathlib import Path

import pytest

from app.services.serpapi.normalizers import normalize_payload

FIXTURES = Path(__file__).parent / "fixtures"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("engine", "fixture", "expected_type"),
    [
        ("google_scholar", "scholar.json", "paper"),
        ("google_patents", "patents.json", "patent"),
        ("google_news", "news.json", "news"),
        ("google", "google.json", "market"),
    ],
)
def test_evidence_normalizers(engine: str, fixture: str, expected_type: str) -> None:
    normalized = normalize_payload(engine, load(fixture))
    assert normalized.search_id
    assert normalized.result_count == 1
    assert normalized.evidence[0].evidence_type == expected_type
    assert normalized.evidence[0].title


def test_scholar_keeps_citation_metadata() -> None:
    normalized = normalize_payload("google_scholar", load("scholar.json"))
    assert normalized.estimated_total_results == 1250
    assert normalized.evidence[0].metadata["citation_count"] == 42


def test_trends_expands_each_value_into_a_point() -> None:
    normalized = normalize_payload("google_trends", load("trends.json"))
    assert normalized.result_count == 6
    assert normalized.trend_points[-1].query == "Event-Based Vision"
    assert normalized.trend_points[-1].value == 25

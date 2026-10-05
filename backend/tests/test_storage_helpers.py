from datetime import UTC

from app.storage.postgres import _float_optional, _parse_datetime, _trend_datetime, _unique_slug


def test_unique_slug_handles_collisions() -> None:
    used: set[str] = set()

    assert _unique_slug("Event-Based Vision", used) == "event-based-vision"
    assert _unique_slug("Event Based Vision", used) == "event-based-vision-2"


def test_parse_datetime_keeps_known_dates_and_rejects_relative_text() -> None:
    parsed = _parse_datetime("2026-10-03")

    assert parsed is not None
    assert parsed.tzinfo == UTC
    assert _parse_datetime("3 hours ago") is None


def test_trend_datetime_prefers_unix_timestamp() -> None:
    parsed = _trend_datetime("1791068400", "Oct 3, 2026")

    assert parsed is not None
    assert parsed.tzinfo == UTC


def test_float_optional_preserves_missing_values() -> None:
    assert _float_optional(None) is None
    assert _float_optional("0.25") == 0.25

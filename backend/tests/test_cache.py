from app.services.serpapi.cache import FileSearchCache, query_fingerprint


def test_fingerprint_is_stable_and_ignores_secrets() -> None:
    left = query_fingerprint("google", {"q": "edge ai", "hl": "en", "api_key": "secret"})
    right = query_fingerprint("google", {"hl": "en", "q": "edge ai", "api_key": "other"})
    assert left == right


def test_file_cache_round_trip(tmp_path) -> None:
    cache = FileSearchCache(tmp_path)
    payload = {"search_metadata": {"id": "abc"}, "organic_results": []}
    params = {"q": "edge ai"}

    fingerprint = cache.put(engine="google", params=params, payload=payload)
    hit = cache.get(engine="google", params=params)

    assert hit is not None
    assert hit.fingerprint == fingerprint
    assert hit.payload == payload

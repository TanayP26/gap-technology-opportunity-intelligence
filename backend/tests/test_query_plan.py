from app.services.serpapi.queries import build_query_plan


def test_six_subdomains_need_two_trend_calls() -> None:
    subdomains = [f"topic {index}" for index in range(6)]
    plan = build_query_plan("parent", subdomains)

    trend_calls = [item for item in plan if item.engine == "google_trends"]

    assert len(trend_calls) == 2
    assert len(plan) == 38
    assert trend_calls[0].target_subdomains == subdomains[:5]
    assert trend_calls[1].target_subdomains == subdomains[5:]


def test_query_plan_keeps_serpapi_usage_material() -> None:
    plan = build_query_plan(
        "neuromorphic computing",
        ["event-based vision", "memristive computing"],
    )
    engines = {item.engine for item in plan}

    assert engines == {
        "google_scholar",
        "google_patents",
        "google_trends",
        "google_news",
        "google",
    }


def test_google_news_query_uses_search_operator_not_advanced_sort() -> None:
    plan = build_query_plan("neuromorphic computing", ["event-based vision"])
    news = next(item for item in plan if item.engine == "google_news")

    assert "so" not in news.params
    assert "when:1y" in news.params["q"]
    assert news.params["q"] == news.query


def test_single_subdomain_searches_keep_target_identity() -> None:
    plan = build_query_plan(
        "neuromorphic computing",
        ["event-based vision", "memristive computing"],
    )
    non_trends = [item for item in plan if item.engine != "google_trends"]

    assert all(len(item.target_subdomains) == 1 for item in non_trends)
    assert {item.target_subdomains[0] for item in non_trends} == {
        "event-based vision",
        "memristive computing",
    }

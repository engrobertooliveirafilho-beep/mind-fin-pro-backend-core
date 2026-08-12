from app.runtime.p2370_institutional_strategy_family_expansion import (
    STRATEGY_FAMILIES,
    OBJECTIVE_PROFILES,
    build_catalog,
)


def test_family_expansion_has_required_families():
    families = {x["family"] for x in STRATEGY_FAMILIES}

    required = {
        "TREND_FOLLOWING",
        "PULLBACK",
        "CORRECTION",
        "REVERSAL",
        "COUNTER_TREND",
        "BREAKOUT",
        "MEAN_REVERSION",
        "LIQUIDITY",
        "SMART_MONEY",
        "SESSION",
        "VOLATILITY",
    }

    assert required.issubset(families)


def test_objective_profiles_are_paper_only():
    for profile in OBJECTIVE_PROFILES:
        assert profile["permission"] == "PAPER_ONLY_CANDIDATE_DISCOVERY"
        assert profile["min_rr"] >= 2.0


def test_catalog_is_generated_without_real_order_permission():
    rows = build_catalog()

    assert len(rows) > 100
    assert all(x["mode"] == "PAPER_ONLY" for x in rows)
    assert all(x["real_orders"] == "FORBIDDEN" for x in rows)
    assert all(x["ftmo_real"] == "FORBIDDEN" for x in rows)
    assert any(x["profile"] == "SCALP" and x["timeframe"] == "M1" for x in rows)
    assert any(x["profile"] == "INTRADAY" and x["timeframe"] == "M5" for x in rows)
    assert any(x["profile"] == "SWING" and x["timeframe"] == "H4" for x in rows)

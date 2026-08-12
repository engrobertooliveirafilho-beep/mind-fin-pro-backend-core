from app.runtime.p2372_de40_parametric_strategy_variation_engine import (
    base_param_grid,
    expand_candidate,
)


def test_base_grid_has_risk_and_filters():
    grid = base_param_grid("PULLBACK", "INTRADAY")

    assert 2.0 in grid["rr_values"]
    assert "session_filters" in grid
    assert "atr_multipliers" in grid
    assert "pullback_depths" in grid


def test_expand_candidate_generates_many_variations():
    row = {
        "symbol": "DE40",
        "family": "PULLBACK",
        "variant": "EMA_PULLBACK",
        "profile": "INTRADAY",
        "timeframe": "M5",
        "target_frequency": "1_WINNING_OPPORTUNITY_PER_DAY_TARGET",
        "min_rr": "2.0",
        "preferred_rr": "3.0",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "status": "CATALOGED_FOR_BACKTEST",
        "warning": "TARGET_FREQUENCY_IS_DISCOVERY_GOAL_NOT_WIN_PROMISE",
    }

    rows = expand_candidate(row)

    assert len(rows) > 100
    assert all(x["mode"] == "PAPER_ONLY" for x in rows)
    assert all(x["real_orders"] == "FORBIDDEN" for x in rows)
    assert all(x["ftmo_real"] == "FORBIDDEN" for x in rows)
    assert any(float(x["rr"]) == 3.0 for x in rows)

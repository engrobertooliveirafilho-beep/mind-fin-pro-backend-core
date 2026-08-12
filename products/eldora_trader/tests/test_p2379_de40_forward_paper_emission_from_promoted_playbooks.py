from app.runtime.p2379_de40_forward_paper_emission_from_promoted_playbooks import (
    infer_direction,
    risk_tier,
    create_signal,
)


def test_infer_direction():
    assert infer_direction("INSTITUTIONAL_DISPLACEMENT_UP", "TREND_UP") == "BUY_PAPER"
    assert infer_direction("LIQUIDITY_SWEEP_REVERSAL_DOWN", "TREND_DOWN") == "SELL_PAPER"


def test_risk_tier_priority():
    row = {
        "profit_factor_proxy": "2.2",
        "expectancy_r_proxy": "0.3",
        "max_drawdown_r_proxy": "10",
        "samples": "100",
    }
    assert risk_tier(row) == "PRIORITY_PAPER"


def test_create_signal_is_paper_only():
    row = {
        "timeframe": "M5",
        "session": "EUROPE_OPEN",
        "regime": "TREND_UP",
        "lifecycle": "INSTITUTIONAL_ENTRY_CONTINUATION",
        "footprint": "INSTITUTIONAL_DISPLACEMENT_UP",
        "family": "TREND_FOLLOWING",
        "samples": "100",
        "profit_factor_proxy": "2.0",
        "expectancy_r_proxy": "0.25",
        "max_drawdown_r_proxy": "10",
        "avg_rr_possible_proxy": "3.2",
    }

    sig = create_signal(row, "PLAYBOOK", 1)

    assert sig["mode"] == "PAPER_ONLY"
    assert sig["real_orders"] == "FORBIDDEN"
    assert sig["ftmo_real"] == "FORBIDDEN"
    assert sig["direction"] == "BUY_PAPER"
    assert sig["mt5_real_permission"] == "DENIED"

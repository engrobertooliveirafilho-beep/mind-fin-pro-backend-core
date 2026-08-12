from app.runtime.p2380_de40_forward_paper_feedback_loop_and_pnl_tracking import (
    direction_mult,
    max_dd,
    aggregate,
)


def test_direction_mult():
    assert direction_mult("BUY_PAPER") == 1
    assert direction_mult("SELL_PAPER") == -1
    assert direction_mult("NO_DIRECTION") == 0


def test_max_dd():
    assert max_dd([1, -2, 1]) == 2


def test_aggregate_promotes_good_family():
    rows = []
    for _ in range(40):
        rows.append({
            "family": "PULLBACK",
            "timeframe": "M5",
            "realized_r": "1.0",
            "mae_r": "0.5",
            "mfe_r": "2.5",
        })

    out = aggregate(rows, ["family", "timeframe"])

    assert out[0]["feedback_decision"] == "PROMOTE_AFTER_FEEDBACK"
    assert out[0]["expectancy_r"] > 0

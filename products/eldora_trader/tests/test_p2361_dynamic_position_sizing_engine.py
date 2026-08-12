from app.runtime.p2361_dynamic_position_sizing_engine import dynamic_paper_lot, health

def test_priority_setup_increases_paper_lot():
    out = dynamic_paper_lot({
        "base_lot": 0.01,
        "institutional_score": 92,
        "expected_payoff": 3.5,
        "current_drawdown": 3,
        "correlation_ok": True,
        "last_trade_loss": False,
    })
    assert out["recommended_paper_lot"] == 0.015
    assert out["real_orders"] == "FORBIDDEN"

def test_bad_setup_blocks_lot():
    out = dynamic_paper_lot({
        "base_lot": 0.01,
        "institutional_score": 40,
        "expected_payoff": 2.0,
        "current_drawdown": 12,
        "correlation_ok": False,
    })
    assert out["recommended_paper_lot"] == 0.0

def test_post_loss_reduces_size():
    out = dynamic_paper_lot({
        "base_lot": 0.01,
        "institutional_score": 80,
        "expected_payoff": 3.2,
        "current_drawdown": 2,
        "correlation_ok": True,
        "last_trade_loss": True,
    })
    assert out["recommended_paper_lot"] <= 0.005

def test_health():
    assert health()["status"] == "OK"

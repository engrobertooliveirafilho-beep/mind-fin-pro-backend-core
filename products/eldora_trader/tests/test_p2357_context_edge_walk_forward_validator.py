from app.runtime.p2357_context_edge_walk_forward_validator import validate_walk_forward, health

def test_walk_forward_rejects_overfit():
    out = validate_walk_forward([
        {
            "context_edge": "TRENDING_BREAKOUT",
            "train_profit_factor": 3.0,
            "test_profit_factor": 0.9,
            "train_payoff": 4.0,
            "test_payoff": 1.2,
            "test_trades": 40,
            "test_max_drawdown": 12,
        }
    ])
    assert out["rejected"] == 1

def test_walk_forward_promotes_robust_context_edge():
    out = validate_walk_forward([
        {
            "context_edge": "TRENDING_BREAKOUT",
            "train_profit_factor": 2.2,
            "test_profit_factor": 1.8,
            "train_payoff": 3.5,
            "test_payoff": 3.1,
            "test_trades": 80,
            "test_max_drawdown": 6,
        }
    ])
    assert out["passed"] == 1
    assert out["passed_rows"][0]["decision"] == "PROMOTE_CONTEXT_EDGE"

def test_health():
    assert health()["status"] == "OK"

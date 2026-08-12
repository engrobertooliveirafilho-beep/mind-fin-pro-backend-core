from app.runtime.p2358_anti_overfit_context_edge_validator import anti_overfit_validate, health

def test_rejects_single_asset_overfit():
    out = anti_overfit_validate({
        "edge_id": "E1",
        "context_edge": "TRENDING_BREAKOUT",
        "symbols_tested": 1,
        "years_tested": 1,
        "regimes_tested": 1,
        "out_of_sample_profit_factor": 3.0,
        "out_of_sample_payoff": 4.0,
        "out_of_sample_expectancy": 1.0,
        "max_drawdown": 5,
        "parameter_sensitivity": 20,
    })
    assert out["anti_overfit_passed"] is False
    assert "LOW_SYMBOL_DIVERSITY" in out["failures"]

def test_promotes_robust_context_edge():
    out = anti_overfit_validate({
        "edge_id": "E2",
        "context_edge": "TRENDING_BREAKOUT",
        "symbols_tested": 5,
        "years_tested": 4,
        "regimes_tested": 4,
        "out_of_sample_profit_factor": 1.8,
        "out_of_sample_payoff": 3.2,
        "out_of_sample_expectancy": 0.4,
        "max_drawdown": 7,
        "parameter_sensitivity": 20,
    })
    assert out["anti_overfit_passed"] is True
    assert out["decision"] == "PROMOTE"

def test_health():
    assert health()["status"] == "OK"

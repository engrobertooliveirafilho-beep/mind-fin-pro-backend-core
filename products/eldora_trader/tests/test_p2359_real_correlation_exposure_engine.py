from app.runtime.p2359_real_correlation_exposure_engine import portfolio_exposure, correlation_precheck, health

def test_detects_hidden_usd_concentration():
    out = portfolio_exposure([
        {"symbol": "EURUSD", "side": "BUY", "lot": 0.01},
        {"symbol": "GBPUSD", "side": "BUY", "lot": 0.01},
        {"symbol": "AUDUSD", "side": "BUY", "lot": 0.01},
    ])
    assert out["concentration"] == "HIGH"
    assert out["decision"] == "REDUCE_OR_BLOCK_CORRELATED_EXPOSURE"
    assert out["real_orders"] == "FORBIDDEN"

def test_blocks_new_correlated_trade():
    out = correlation_precheck(
        [
            {"symbol": "EURUSD", "side": "BUY", "lot": 0.01},
            {"symbol": "GBPUSD", "side": "BUY", "lot": 0.01},
        ],
        {"symbol": "AUDUSD", "side": "BUY", "lot": 0.01}
    )
    assert out["approved"] is False
    assert out["decision"] == "BLOCK_CORRELATED_EXPOSURE"

def test_health():
    assert health()["status"] == "OK"

from app.runtime.p2355_multi_year_multi_asset_backtest_optimizer import optimize, health

def test_optimizer_promotes_only_robust_edges():
    out = optimize([
        {"symbol":"EURUSD","style":"SCALP","timeframe":"M5","strategy":"TREND_EMA","trades":120,"win_rate":62,"payoff":3.2,"profit_factor":2.1,"max_drawdown":6,"expectancy":0.8},
        {"symbol":"GBPUSD","style":"DAY_TRADE","timeframe":"M15","strategy":"MEAN_REVERSION","trades":80,"win_rate":45,"payoff":1.5,"profit_factor":0.9,"max_drawdown":18,"expectancy":-0.2},
    ])
    assert out["candidates_total"] == 2
    assert out["promoted"] == 1
    assert out["ranking"][0]["decision"] == "PROMOTE_TO_FORWARD_PAPER"
    assert out["real_orders"] == "FORBIDDEN"

def test_health():
    assert health()["status"] == "OK"

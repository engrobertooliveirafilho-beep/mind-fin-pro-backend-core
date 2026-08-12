from app.p1621k_video_strategy_backtest_executor.engine import run, sma_cross_backtest

def test_p1621k_backtest_metrics():
    m=sma_cross_backtest([1+i*0.01 for i in range(200)])
    assert "profit_factor" in m
    assert "trades" in m

def test_p1621k_run_blocks_live():
    r=run()
    assert r["STATUS"]=="P16.21K_VIDEO_STRATEGY_BACKTEST_EXECUTOR_IMPLEMENTED"
    assert r["LIVE"]=="FORBIDDEN"
    assert r["REAL_ORDERS"]=="FORBIDDEN"

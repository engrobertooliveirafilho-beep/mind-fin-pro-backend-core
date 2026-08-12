from app.p1621l_video_strategy_wf_mc.engine import run, walk_forward, monte_carlo

def test_p1621l_wf_mc():
    x={"dataset":"d","backtest_metrics":{"profit_factor":2,"trades":40,"max_drawdown":0.1}}
    assert walk_forward(x)["walk_forward_status"]=="WALK_FORWARD_APPROVED"
    assert "monte_carlo_status" in monte_carlo(x)

def test_p1621l_run_blocks_live():
    r=run()
    assert r["STATUS"]=="P16.21L_VIDEO_STRATEGY_WALK_FORWARD_MONTE_CARLO_IMPLEMENTED"
    assert r["LIVE"]=="FORBIDDEN"
    assert r["REAL_ORDERS"]=="FORBIDDEN"

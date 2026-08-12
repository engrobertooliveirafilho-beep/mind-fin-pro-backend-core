from pathlib import Path
from mind_trader.app.validation.edge_validation import trade_metrics, monte_carlo, degradation_test, cost_stress_test, validate_backtest_trades, save_validation_report

def test_trade_metrics_rejects_empty():
    m=trade_metrics([])
    assert m["trades"]==0
    assert m["profit_factor"]==0

def test_losing_edge_rejected():
    trades=[{"pnl":-1} for _ in range(20)]
    r=validate_backtest_trades(trades)
    assert r["classification"]=="REJECTED_EDGE"
    assert r["production"]=="BLOCKED"

def test_weak_edge_not_production():
    trades=[{"pnl":2 if i%2==0 else -1.8} for i in range(40)]
    r=validate_backtest_trades(trades)
    assert r["classification"] in ["RESEARCH_CANDIDATE","REJECTED_EDGE"]
    assert r["production"]=="BLOCKED"

def test_strong_edge_can_only_be_paper_candidate():
    trades=[{"pnl":3 if i%3 else -1} for i in range(60)]
    r=validate_backtest_trades(trades)
    assert r["classification"] in ["PAPER_TRADING_CANDIDATE","RESEARCH_CANDIDATE"]
    assert r["production"]=="BLOCKED"
    assert r["edge_claim"]=="NONE_UNTIL_PAPER_AND_LIVE_EVIDENCE"

def test_monte_carlo_real_runs():
    trades=[{"pnl":3 if i%3 else -1} for i in range(60)]
    r=monte_carlo(trades,runs=50)
    assert r["runs"]==50
    assert "p05_net_profit" in r

def test_degradation_and_cost_stress():
    trades=[{"pnl":3 if i%3 else -1} for i in range(60)]
    assert "passed" in degradation_test(trades)
    assert "passed" in cost_stress_test(trades)

def test_save_validation_report(tmp_path):
    out=save_validation_report({"ok":True},str(tmp_path/"edge.json"))
    assert Path(out).exists()

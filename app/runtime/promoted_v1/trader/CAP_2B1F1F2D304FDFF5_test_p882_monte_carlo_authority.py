from pathlib import Path
from mind_trader.app.validation.monte_carlo_authority import monte_carlo_authority

def test_monte_carlo_insufficient_trades():
    r=monte_carlo_authority([{"pnl":1}],runs=10)
    assert r["passed"] is False
    assert r["decision"]=="MONTE_CARLO_INSUFFICIENT_TRADES"

def test_monte_carlo_pass_or_retest_research_only():
    trades=[{"pnl":3 if i%3 else -1} for i in range(80)]
    r=monte_carlo_authority(trades,runs=100,max_dd_allowed=40)
    assert r["decision"] in ["MONTE_CARLO_PASS_RESEARCH_ONLY","MONTE_CARLO_REJECT_OR_RETEST"]
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"
    assert r["edge_claim"]=="NONE"

def test_monte_carlo_rejects_weak_distribution():
    trades=[{"pnl":1 if i%2 else -3} for i in range(80)]
    r=monte_carlo_authority(trades,runs=100,max_dd_allowed=40)
    assert r["passed"] is False

def test_monte_carlo_report_written():
    trades=[{"pnl":3 if i%3 else -1} for i in range(80)]
    monte_carlo_authority(trades,runs=50,max_dd_allowed=40)
    assert Path("mind_trader/reports/P8.82_monte_carlo_authority.json").exists()

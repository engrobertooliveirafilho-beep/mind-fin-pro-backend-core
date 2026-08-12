from pathlib import Path
from mind_trader.app.risk.capital_evolution import fixed_fractional_risk, position_size, drawdown_adjusted_risk, approximate_risk_of_ruin, capital_plan, save_capital_report

def test_fixed_fractional_risk():
    r=fixed_fractional_risk(100000,0.01)
    assert r["risk_amount"]==1000
    assert r["decision"]=="RISK_OK"

def test_position_size_blocks_invalid_stop():
    r=position_size(100,100,500)
    assert r["decision"]=="BLOCK_INVALID_STOP_OR_RISK"

def test_drawdown_kill_switch():
    r=drawdown_adjusted_risk(89000,100000)
    assert r["decision"]=="KILL_SWITCH_DRAWDOWN"
    assert r["risk_pct"]==0

def test_risk_of_ruin_blocks_negative_edge():
    r=approximate_risk_of_ruin(0.3,1.0,0.005)
    assert r["decision"]=="RUIN_HIGH"

def test_capital_plan_allows_only_simulated_size():
    r=capital_plan(100000,100000,100,98,0.6,1.5)
    assert r["decision"] in ["ALLOW_SIMULATED_SIZE","BLOCK_TRADE"]
    assert r["production"]=="BLOCKED"
    assert r["edge_claim"]=="NONE"

def test_capital_plan_blocks_drawdown():
    r=capital_plan(88000,100000,100,98,0.6,1.5)
    assert r["decision"]=="BLOCK_TRADE"
    assert r["reason"]=="KILL_SWITCH_DRAWDOWN"

def test_save_capital_report(tmp_path):
    out=save_capital_report({"ok":True},str(tmp_path/"cap.json"))
    assert Path(out).exists()

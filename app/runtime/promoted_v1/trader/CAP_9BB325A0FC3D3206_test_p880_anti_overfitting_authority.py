from pathlib import Path
from mind_trader.app.validation.anti_overfitting_authority import parameter_sensitivity, randomization_test, anti_overfitting_authority

def test_parameter_sensitivity_runs():
    r=parameter_sensitivity([{"expectancy":1},{"expectancy":1.2},{"expectancy":0.9}])
    assert "passed" in r
    assert r["mean_expectancy"]>0

def test_randomization_blocks_low_trades():
    r=randomization_test([{"pnl":1}])
    assert r["passed"] is False

def test_anti_overfitting_authority_blocks_or_passes_research_only():
    trades=[{"pnl":3 if i%3 else -1} for i in range(60)]
    params=[{"expectancy":1.0},{"expectancy":1.1},{"expectancy":0.95}]
    r=anti_overfitting_authority("g1",trades,params)
    assert r["decision"] in ["ANTI_OVERFITTING_PASS_RESEARCH_ONLY","ANTI_OVERFITTING_REJECT_OR_RETEST"]
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"
    assert r["edge_claim"]=="NONE"

def test_anti_overfitting_report_written():
    trades=[{"pnl":3 if i%3 else -1} for i in range(60)]
    anti_overfitting_authority("g1",trades,[{"expectancy":1},{"expectancy":1.1}])
    assert Path("mind_trader/reports/P8.80_anti_overfitting_authority.json").exists()

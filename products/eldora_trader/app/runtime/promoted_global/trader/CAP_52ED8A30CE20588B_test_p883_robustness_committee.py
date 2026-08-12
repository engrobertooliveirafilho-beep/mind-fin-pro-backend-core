from pathlib import Path
from mind_trader.app.validation.robustness_committee import robustness_committee

def strong_validation():
    return {"out_of_sample":{"trades":80,"profit_factor":2.2,"expectancy":2,"max_drawdown":5},"monte_carlo":{"passed":True},"degradation":{"passed":True},"cost_stress":{"passed":True}}

def test_robustness_committee_research_only():
    trades=[{"pnl":3 if i%3 else -1} for i in range(80)]
    windows=[
        {"expectancy":1,"profit_factor":1.3},
        {"expectancy":0.8,"profit_factor":1.2},
        {"expectancy":0.5,"profit_factor":1.1}
    ]
    params=[{"expectancy":1},{"expectancy":1.1},{"expectancy":0.9}]
    r=robustness_committee("g1",trades,windows,params,strong_validation())
    assert r["decision"] in ["ROBUSTNESS_PASS_PAPER_CANDIDATE","ROBUSTNESS_REJECT_OR_RETEST"]
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"
    assert r["edge_claim"]=="NONE"

def test_robustness_committee_rejects_bad():
    trades=[{"pnl":-1} for _ in range(30)]
    windows=[{"expectancy":-1,"profit_factor":0.8},{"expectancy":-1,"profit_factor":0.9},{"expectancy":-1,"profit_factor":0.7}]
    params=[{"expectancy":-1},{"expectancy":-2}]
    r=robustness_committee("g2",trades,windows,params,strong_validation())
    assert r["decision"]=="ROBUSTNESS_REJECT_OR_RETEST"
    assert r["passed"] is False

def test_robustness_report_written():
    trades=[{"pnl":3 if i%3 else -1} for i in range(80)]
    windows=[{"expectancy":1,"profit_factor":1.3},{"expectancy":1,"profit_factor":1.2},{"expectancy":1,"profit_factor":1.1}]
    robustness_committee("g1",trades,windows,[{"expectancy":1}],strong_validation())
    assert Path("mind_trader/reports/P8.83_robustness_committee.json").exists()

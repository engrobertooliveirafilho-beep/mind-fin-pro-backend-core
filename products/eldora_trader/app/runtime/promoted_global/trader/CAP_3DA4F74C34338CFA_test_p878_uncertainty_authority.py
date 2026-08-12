from pathlib import Path
from mind_trader.app.engines.uncertainty_authority import uncertainty_score, uncertainty_authority

def strong_report():
    return {"out_of_sample":{"trades":80,"profit_factor":2.2,"expectancy":2,"max_drawdown":5},"monte_carlo":{"passed":True},"degradation":{"passed":True},"cost_stress":{"passed":True}}

def weak_report():
    return {"out_of_sample":{"trades":3,"profit_factor":0.9,"expectancy":-1,"max_drawdown":50},"monte_carlo":{"passed":False},"degradation":{"passed":False},"cost_stress":{"passed":False}}

def test_uncertainty_accepts_strong_research():
    r=uncertainty_score(strong_report())
    assert r["decision"]=="UNCERTAINTY_ACCEPT_RESEARCH"
    assert r["confidence"]>=0.75

def test_uncertainty_blocks_weak():
    r=uncertainty_score(weak_report())
    assert r["decision"]=="UNCERTAINTY_BLOCK"
    assert r["production"]=="BLOCKED"

def test_uncertainty_authority_report_written():
    r=uncertainty_authority("g1",strong_report())
    assert r["paper_candidate_allowed"] is True
    assert r["live"]=="FORBIDDEN"
    assert Path("mind_trader/reports/P8.78_uncertainty_authority.json").exists()

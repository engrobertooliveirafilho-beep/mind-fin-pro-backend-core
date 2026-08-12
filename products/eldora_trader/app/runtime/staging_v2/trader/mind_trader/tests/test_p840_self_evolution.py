from pathlib import Path
from mind_trader.app.engines.self_evolution import score_validation, detect_deterioration, evolve_genome, evolve_portfolio, save_self_evolution_report

def good_report():
    return {"classification":"PAPER_TRADING_CANDIDATE","out_of_sample":{"expectancy":2,"profit_factor":1.8,"max_drawdown":5},"monte_carlo":{"passed":True},"degradation":{"passed":True},"cost_stress":{"passed":True}}

def bad_report():
    return {"classification":"REJECTED_EDGE","out_of_sample":{"expectancy":-1,"profit_factor":0.8,"max_drawdown":20},"monte_carlo":{"passed":False},"degradation":{"passed":False},"cost_stress":{"passed":False}}

def test_score_validation_good_positive():
    assert score_validation(good_report()) > 80

def test_score_validation_bad_low():
    assert score_validation(bad_report()) < 0

def test_detect_deterioration_three_step_decay():
    r=detect_deterioration([{"score":100},{"score":70},{"score":40}])
    assert r["deteriorated"] is True

def test_evolve_genome_paper_candidate_only():
    r=evolve_genome("g1",good_report())
    assert r["status"]=="PAPER_CANDIDATE_ONLY"
    assert r["production"]=="BLOCKED"
    assert r["edge_claim"]=="NONE"

def test_evolve_genome_demotes_deterioration():
    r=evolve_genome("g1",good_report(),[{"score":400},{"score":300}])
    assert r["status"]=="DEMOTED_RESEARCH_REVIEW"

def test_evolve_portfolio_research_only():
    r=evolve_portfolio({"g1":good_report(),"g2":bad_report()})
    assert r["evaluated"]==2
    assert r["decision"]=="SELF_EVOLUTION_RESEARCH_ONLY"
    assert r["production"]=="BLOCKED"

def test_save_self_evolution_report(tmp_path):
    out=save_self_evolution_report({"ok":True},str(tmp_path/"self.json"))
    assert Path(out).exists()


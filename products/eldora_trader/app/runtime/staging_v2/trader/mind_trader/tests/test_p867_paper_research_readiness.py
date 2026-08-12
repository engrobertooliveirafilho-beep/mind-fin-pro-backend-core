from pathlib import Path
from mind_trader.app.audits.paper_research_readiness import paper_research_readiness, save_paper_research_readiness

def test_paper_research_ready():
    r=paper_research_readiness(tests_passed=188)
    assert r["decision"]=="PAPER_RESEARCH_READY"
    assert r["allowed_scope"]=="PAPER_RESEARCH_ONLY"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"
    assert r["edge_claim"]=="NONE"

def test_paper_research_not_ready_on_failed_check():
    r=paper_research_readiness({"data_connector":False},188)
    assert r["decision"]=="PAPER_RESEARCH_NOT_READY"
    assert "data_connector" in r["failed"]

def test_save_paper_research_readiness(tmp_path):
    r=save_paper_research_readiness(str(tmp_path/"ready.json"),tests_passed=188)
    assert Path(tmp_path/"ready.json").exists()
    assert r["causality_claim"]=="NOT_PROVEN"

from pathlib import Path
from mind_trader.app.audits.final_research_certification import final_research_certification, REQUIRED_CERT

def test_final_research_certified_paper_only():
    r=final_research_certification(tests_passed=266)
    assert r["decision"]=="FINAL_RESEARCH_CERTIFIED_PAPER_ONLY"
    assert r["allowed_scope"]=="PAPER_RESEARCH_ONLY"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"
    assert r["edge_claim"]=="NONE"
    assert r["causality_claim"]=="NOT_PROVEN"

def test_final_research_certification_fails_missing():
    checks={k:True for k in REQUIRED_CERT}
    checks.pop("robustness_committee")
    r=final_research_certification(checks,266)
    assert r["decision"]=="FINAL_RESEARCH_CERTIFICATION_FAILED"
    assert "robustness_committee" in r["missing"]

def test_final_research_certification_fails_failed_check():
    checks={k:True for k in REQUIRED_CERT}
    checks["monte_carlo_authority"]=False
    r=final_research_certification(checks,266)
    assert r["decision"]=="FINAL_RESEARCH_CERTIFICATION_FAILED"
    assert "monte_carlo_authority" in r["failed"]

def test_final_research_certification_report_written():
    final_research_certification(tests_passed=266)
    assert Path("mind_trader/reports/P8.90_final_research_certification.json").exists()

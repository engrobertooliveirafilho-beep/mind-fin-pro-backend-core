from pathlib import Path
from mind_trader.app.validation.validation_protocol_engine import REQUIRED_EVIDENCE, validate_evidence_package, force_block_forbidden_decision, validation_committee_report, save_validation_committee_report

def full_package(value=True):
    return {k:value for k in REQUIRED_EVIDENCE}

def test_incomplete_evidence_blocks():
    r=validate_evidence_package({"edge_validation":True})
    assert r["decision"]=="INCOMPLETE_EVIDENCE"
    assert r["production"]=="BLOCKED"
    assert "walk_forward" in r["missing"]

def test_failed_evidence_rejected():
    p=full_package(True)
    p["monte_carlo"]=False
    r=validate_evidence_package(p)
    assert r["decision"]=="REJECTED_EDGE"
    assert "monte_carlo" in r["failed"]

def test_full_evidence_caps_at_paper_only():
    r=validate_evidence_package(full_package(True))
    assert r["decision"]=="PAPER_TRADING_APPROVED"
    assert r["approved_scope"]=="PAPER_ONLY"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"

def test_forbidden_live_approval_force_blocked():
    r=force_block_forbidden_decision("LIVE_APPROVED")
    assert r["decision"]=="FORCE_BLOCK"
    assert r["production"]=="BLOCKED"

def test_dict_evidence_passes():
    p={k:{"passed":True} for k in REQUIRED_EVIDENCE}
    r=validate_evidence_package(p)
    assert r["decision"]=="PAPER_TRADING_APPROVED"

def test_committee_report_structure():
    r=validation_committee_report("g1",full_package(True))
    assert r["committee"]=="P8.84_VALIDATION_PROTOCOL_WITH_ROBUSTNESS"
    assert r["result"]["decision"]=="PAPER_TRADING_APPROVED"
    assert r["live"]=="FORBIDDEN"

def test_save_validation_committee_report(tmp_path):
    out=save_validation_committee_report({"ok":True},str(tmp_path/"committee.json"))
    assert Path(out).exists()


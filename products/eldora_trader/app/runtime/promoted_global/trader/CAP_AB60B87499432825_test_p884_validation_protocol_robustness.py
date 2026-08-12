from pathlib import Path
from mind_trader.app.validation.validation_protocol_engine import REQUIRED_EVIDENCE, validate_evidence_package, validation_committee_report, save_validation_committee_report

def full_package(value=True):
    return {k:value for k in REQUIRED_EVIDENCE}

def test_requires_robustness_committee():
    p=full_package(True)
    p.pop("robustness_committee")
    r=validate_evidence_package(p)
    assert r["decision"]=="INCOMPLETE_EVIDENCE"
    assert "robustness_committee" in r["missing"]

def test_rejects_failed_robustness_committee():
    p=full_package(True)
    p["robustness_committee"]={"decision":"ROBUSTNESS_REJECT_OR_RETEST","passed":False}
    r=validate_evidence_package(p)
    assert r["decision"]=="REJECTED_EDGE"
    assert "robustness_committee" in r["failed"]

def test_accepts_robustness_committee_paper_only():
    p=full_package(True)
    p["robustness_committee"]={"decision":"ROBUSTNESS_PASS_PAPER_CANDIDATE","passed":True}
    r=validate_evidence_package(p)
    assert r["decision"]=="PAPER_TRADING_APPROVED"
    assert r["approved_scope"]=="PAPER_ONLY"
    assert r["production"]=="BLOCKED"

def test_validation_committee_report_v84():
    p=full_package(True)
    p["robustness_committee"]={"decision":"ROBUSTNESS_PASS_PAPER_CANDIDATE","passed":True}
    r=validation_committee_report("g1",p)
    assert r["committee"]=="P8.84_VALIDATION_PROTOCOL_WITH_ROBUSTNESS"
    assert r["live"]=="FORBIDDEN"

def test_save_validation_committee_report(tmp_path):
    p=save_validation_committee_report({"ok":True},str(tmp_path/"v.json"))
    assert Path(p).exists()

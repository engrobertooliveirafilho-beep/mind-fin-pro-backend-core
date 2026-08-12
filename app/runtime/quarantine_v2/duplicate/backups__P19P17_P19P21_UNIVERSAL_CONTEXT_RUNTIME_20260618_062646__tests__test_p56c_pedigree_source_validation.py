from app.mind.p5_6c_pedigree_source_validation import run_p56c_healthcheck
from app.mind.p5_6c_pedigree_source_validation.validator import evidence_score, status_from_score

def test_healthcheck():
    assert run_p56c_healthcheck()["status"]=="P5.6C_READY"

def test_evidence_score():
    assert evidence_score({"text":"sire dam ABBI registry"}) >= 70

def test_status():
    assert status_from_score(80)=="validated"
    assert status_from_score(50)=="needs_review"
    assert status_from_score(10)=="blocked_low_evidence"

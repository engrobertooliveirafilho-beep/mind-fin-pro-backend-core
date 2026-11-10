"""Regression tests for R278 fail-closed research quarantine."""
from mind_trader.security.et665_r278_quarantine import evaluate

BASE = {"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
        "real_execution_allowed":False,"lineage":["P2401_MULTI_EDGE_WALK_FORWARD_DD_FILTER"]}

def test_synthetic_lineage_quarantined():
    r = evaluate(BASE)
    assert not r.allowed and r.status == "QUARANTINE"

def test_missing_lineage_never_promotes():
    r = evaluate({**BASE,"lineage":[]})
    assert not r.allowed and r.status == "OBSERVE_ONLY"

def test_real_mode_blocked():
    r = evaluate({**BASE,"mode":"LIVE"})
    assert not r.allowed and r.status == "BLOCK"

def test_no_execution_denial_blocked():
    r = evaluate({**BASE,"real_execution_allowed":True})
    assert not r.allowed and r.status == "BLOCK"

def test_unrelated_lineage_still_requires_causal_certification():
    r = evaluate({**BASE,"lineage":["P2388"]})
    assert not r.allowed and r.status == "OBSERVE_ONLY"

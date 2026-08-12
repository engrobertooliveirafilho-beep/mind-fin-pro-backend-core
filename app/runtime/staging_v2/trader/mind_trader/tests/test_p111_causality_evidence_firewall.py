from app.p11_causality_evidence_firewall.engine import evaluate_causality_claim, firewall, run, REQUIRED_CAUSALITY_TESTS

def test_p111_accepts_only_full_causality_evidence_paper_only():
    e=evaluate_causality_claim({"claim_id":"x","tests":{t:True for t in REQUIRED_CAUSALITY_TESTS}})
    assert e["causality_proven"] is True
    assert e["live_allowed"] is False
    assert e["promotion_allowed"] is False

def test_p111_rejects_partial_causality():
    e=evaluate_causality_claim({"claim_id":"x","tests":{"temporal_precedence":True}})
    assert e["causality_proven"] is False
    assert e["status"]=="CAUSALITY_NOT_PROVEN"

def test_p111_firewall_blocks_candidate_promotion():
    c=firewall({"candidate_id":"c1","causality_claim":{"claim_id":"x","tests":{t:True for t in REQUIRED_CAUSALITY_TESTS}}})
    assert c["promotion_allowed"] is False
    assert c["live_allowed"] is False

def test_p111_manifest():
    m=run()
    assert m["STATUS"]=="P11.1_CAUSALITY_EVIDENCE_FIREWALL_IMPLEMENTED"
    assert m["EXPORT_READY"] is True

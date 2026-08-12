from app.p11_evidence_promotion_gate.engine import evaluate_paper_promotion, run
from app.p11_causality_evidence_firewall.engine import REQUIRED_CAUSALITY_TESTS

def full_candidate():
    return {
        "candidate_id":"x",
        "edge_candidate":{"candidate_id":"e","datasets":[{"asset":"WIN","period":"2024"},{"asset":"WIN","period":"2025"},{"asset":"WDO","period":"2026"}],"walk_forward_results":[True,True,True],"monte_carlo_results":[True,True,True],"robustness_score":0.9,"out_of_sample_score":0.8},
        "causality_claim":{"claim_id":"c","tests":{t:True for t in REQUIRED_CAUSALITY_TESTS}}
    }

def test_p112_allows_only_paper_promotion():
    r=evaluate_paper_promotion(full_candidate())
    assert r["paper_promotion_allowed"] is True
    assert r["live_promotion_allowed"] is False
    assert r["real_broker_allowed"] is False

def test_p112_blocks_weak_candidate():
    r=evaluate_paper_promotion({"candidate_id":"bad"})
    assert r["paper_promotion_allowed"] is False
    assert r["status"]=="PROMOTION_BLOCKED_INSUFFICIENT_EVIDENCE"

def test_p112_manifest():
    m=run()
    assert m["STATUS"]=="P11.2_EVIDENCE_PROMOTION_GATE_IMPLEMENTED"
    assert m["LIVE_PROMOTION_ALLOWED"] is False
    assert m["EXPORT_READY"] is True

from app.p11_edge_evidence_engine.engine import evaluate_edge_evidence, run

def test_p11_accepts_only_full_paper_evidence():
    c={"candidate_id":"x","datasets":[{"asset":"WIN","period":"2024"},{"asset":"WIN","period":"2025"},{"asset":"WDO","period":"2026"}],"walk_forward_results":[True,True,True],"monte_carlo_results":[True,True,True],"robustness_score":0.9,"out_of_sample_score":0.8}
    e=evaluate_edge_evidence(c)
    assert e["paper_edge_evidence"] is True
    assert e["live_allowed"] is False
    assert e["promotion_allowed"] is False

def test_p11_rejects_weak_evidence():
    e=evaluate_edge_evidence({"candidate_id":"bad","datasets":[]})
    assert e["paper_edge_evidence"] is False
    assert e["status"]=="INSUFFICIENT_EVIDENCE"

def test_p11_manifest():
    m=run()
    assert m["STATUS"]=="P11_EDGE_EVIDENCE_ENGINE_IMPLEMENTED"
    assert m["PROMOTION_ALLOWED"] is False
    assert m["EXPORT_READY"] is True

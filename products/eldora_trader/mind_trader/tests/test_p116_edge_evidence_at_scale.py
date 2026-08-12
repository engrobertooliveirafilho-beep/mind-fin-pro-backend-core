from app.p11_edge_evidence_at_scale.engine import evaluate_scale_readiness, run

def test_p116_blocks_without_enough_queued_jobs():
    r=evaluate_scale_readiness({"total_jobs":100,"queued":0})
    assert r["scale_ready"] is False
    assert r["promotion_allowed"] is False

def test_p116_ready_when_coverage_exists_but_still_blocks_live():
    r=evaluate_scale_readiness({"total_jobs":100,"queued":50})
    assert r["scale_ready"] is True
    assert r["live"]=="FORBIDDEN"
    assert r["real_broker"]=="DISABLED"

def test_p116_manifest():
    m=run()
    assert m["STATUS"]=="P11.6_EDGE_EVIDENCE_AT_SCALE_IMPLEMENTED"
    assert m["EDGE"]=="NOT_PROVEN"
    assert m["EXPORT_READY"] is True

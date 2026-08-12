from app.p10_distributed_research_scale.engine import make_job, build_plan, run

def test_p101_job_blocks_live():
    j=make_job("backtest",{"x":1})
    assert j["live"]=="FORBIDDEN"
    assert j["real_broker"]=="DISABLED"
    assert j["promotion_allowed"] is False

def test_p101_plan_has_core_queues():
    jobs=build_plan(2,2000)
    qs={j["queue"] for j in jobs}
    for q in ["ingestion","quality_gate","backtest","walk_forward","monte_carlo","robustness","ranking","reporting"]:
        assert q in qs

def test_p101_manifest():
    m=run()
    assert m["STATUS"]=="P10.1_DISTRIBUTED_RESEARCH_SCALE_IMPLEMENTED"
    assert m["EXPORT_READY"] is True

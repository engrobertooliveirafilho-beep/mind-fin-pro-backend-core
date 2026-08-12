from app.p11_multi_market_research_grid.engine import build_grid, summarize, run

def test_p115_grid_creates_jobs():
    jobs=build_grid(batch_size=1000,batches=2)
    assert len(jobs) > 0
    assert all(j["live"]=="FORBIDDEN" for j in jobs)
    assert all(j["real_broker"]=="DISABLED" for j in jobs)

def test_p115_grid_blocks_without_certified_data():
    jobs=build_grid(batch_size=1000,batches=1)
    s=summarize(jobs)
    assert s["blocked_missing_certified_data"] == s["total_jobs"]
    assert s["queued"] == 0

def test_p115_manifest():
    m=run()
    assert m["STATUS"]=="P11.5_MULTI_MARKET_RESEARCH_GRID_IMPLEMENTED"
    assert m["EXPORT_READY"] is True

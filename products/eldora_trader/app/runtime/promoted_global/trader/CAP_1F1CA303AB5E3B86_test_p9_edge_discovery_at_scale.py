from app.p9_edge_discovery_at_scale.p9_engine import run, live_lock, make_genomes

def test_p9_live_lock():
    s=live_lock()
    assert s["live"]=="FORBIDDEN"
    assert s["real_broker"]=="DISABLED"
    assert s["paper_only"] is True

def test_p9_genome_generation():
    g=make_genomes(100)
    assert len(g)==100
    assert len({x["genome_id"] for x in g})==100

def test_p9_run_snapshot():
    s=run()["P9_STATE_SNAPSHOT"]
    assert s["BASE"]=="P8.100_PAPER_RESEARCH_V1_CERTIFIED"
    assert s["EDGE"]=="NONE_PROVEN"
    assert s["EXPORT_READY"] is True

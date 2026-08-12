from app.p1621b_youtube_absorption_engine.engine import run, discover_video_hypotheses, load_sources

def test_p1621b_sources_include_loop_queries():
    s=load_sources()
    assert any("swing+trader" in x for x in s)
    assert any("trade+criptomoedas" in x for x in s)

def test_p1621b_hypotheses_are_only_hypotheses():
    h=discover_video_hypotheses()
    assert len(h)>=100
    assert all(x["status"]=="HYPOTHESIS_ONLY" for x in h)

def test_p1621b_report_blocks_live():
    r=run()
    assert r["STATUS"]=="P16.21B_YOUTUBE_ABSORPTION_ENGINE_IMPLEMENTED"
    assert r["REAL_ORDERS"]=="FORBIDDEN"
    assert r["LIVE"]=="FORBIDDEN"

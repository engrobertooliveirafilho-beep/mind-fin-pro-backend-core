from app.p1621m_video_edge_memory_merge.engine import run, normalize_video_edge

def test_p1621m_normalize_video_edge():
    e=normalize_video_edge({"dataset":"d","normalized_family":"RSI","normalized_asset":"WINFUT","normalized_timeframe":"H1","backtest_metrics":{"profit_factor":2,"trades":20}})
    assert e["certification_status"]=="PAPER_RESEARCH_CERTIFIED"
    assert e["LIVE"]=="FORBIDDEN"

def test_p1621m_run_blocks_live():
    r=run()
    assert r["STATUS"]=="P16.21M_VIDEO_EDGE_MEMORY_MERGE_IMPLEMENTED"
    assert r["REAL_ORDERS"]=="FORBIDDEN"

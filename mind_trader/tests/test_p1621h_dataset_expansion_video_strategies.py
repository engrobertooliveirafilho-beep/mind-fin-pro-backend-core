from app.p1621h_dataset_expansion_video_strategies.engine import run, required_dataset_matrix

def test_p1621h_required_matrix():
    m=required_dataset_matrix()
    assert len(m)>=40
    assert any(x["asset"]=="WINFUT" for x in m)

def test_p1621h_run_blocks_live():
    r=run()
    assert r["STATUS"]=="P16.21H_DATASET_EXPANSION_FOR_VIDEO_STRATEGIES_IMPLEMENTED"
    assert r["LIVE"]=="FORBIDDEN"
    assert r["REAL_ORDERS"]=="FORBIDDEN"

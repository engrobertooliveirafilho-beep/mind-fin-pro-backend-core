from app.p1621e_real_video_fetch_loop.engine import classify_text, run

def test_p1621e_classify_assets():
    c=classify_text("setup mini índice com vwap e rsi")
    assert "WINFUT" in c["assets"]
    assert "VWAP" in c["families"]

def test_p1621e_run_blocks_live():
    r=run()
    assert r["STATUS"]=="P16.21E_REAL_VIDEO_FETCH_LOOP_IMPLEMENTED"
    assert r["LIVE"]=="FORBIDDEN"
    assert r["REAL_ORDERS"]=="FORBIDDEN"

from app.p1621c_video_transcript_extraction_auto_backtest.engine import run, extract_strategy

def test_p1621c_extracts_strategy_as_hypothesis_only():
    s=extract_strategy({"hypothesis_id":"x","source_url":"u","keyword":"rsi"})
    assert s["family"]=="RSI"
    assert s["status"]=="HYPOTHESIS_ONLY"

def test_p1621c_blocks_live():
    r=run()
    assert r["STATUS"]=="P16.21C_VIDEO_TRANSCRIPT_EXTRACTION_AUTO_BACKTEST_IMPLEMENTED"
    assert r["LIVE"]=="FORBIDDEN"
    assert r["REAL_ORDERS"]=="FORBIDDEN"

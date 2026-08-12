from app.p1621f_transcript_download_strategy_extraction.engine import extract_rules, run

def test_p1621f_extract_rules():
    r=extract_rules("setup com rsi vwap stop alvo rompimento",{})
    assert "RSI_SIGNAL" in r
    assert "VWAP_FILTER" in r
    assert "BREAKOUT" in r

def test_p1621f_run_blocks_live():
    r=run()
    assert r["STATUS"]=="P16.21F_TRANSCRIPT_DOWNLOAD_STRATEGY_EXTRACTION_IMPLEMENTED"
    assert r["LIVE"]=="FORBIDDEN"
    assert r["REAL_ORDERS"]=="FORBIDDEN"

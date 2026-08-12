from app.p1621d_real_transcript_fetcher_dataset_matcher.engine import run, classify_asset, classify_timeframe, enrich_strategy

def test_p1621d_asset_classifier():
    assert classify_asset("mini índice day trade")=="WINFUT"
    assert classify_asset("trade criptomoedas btc")=="BTC"

def test_p1621d_timeframe_classifier():
    assert classify_timeframe("setup 15 minutos")=="M15"
    assert classify_timeframe("grafico h1")=="H1"

def test_p1621d_blocks_live():
    r=run()
    assert r["STATUS"]=="P16.21D_REAL_TRANSCRIPT_FETCHER_AND_DATASET_MATCHER_IMPLEMENTED"
    assert r["LIVE"]=="FORBIDDEN"
    assert r["REAL_ORDERS"]=="FORBIDDEN"

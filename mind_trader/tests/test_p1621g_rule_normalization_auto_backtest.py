from app.p1621g_rule_normalization_auto_backtest.engine import normalize_rule, run

def test_p1621g_normalize_rule():
    s=normalize_rule({"extracted_rules":["RSI_SIGNAL"],"assets":["WINFUT"]})
    assert s["normalized_family"]=="RSI"
    assert s["status"]=="HYPOTHESIS_ONLY"

def test_p1621g_run_blocks_live():
    r=run()
    assert r["STATUS"]=="P16.21G_RULE_NORMALIZATION_AUTO_BACKTEST_IMPLEMENTED"
    assert r["LIVE"]=="FORBIDDEN"
    assert r["REAL_ORDERS"]=="FORBIDDEN"

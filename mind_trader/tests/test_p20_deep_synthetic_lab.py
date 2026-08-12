from app.p20_deep_synthetic_lab.engine import run, indicator_composer, synthetic_strategy_generator

def test_p20_indicator_composer():
    c=indicator_composer()
    assert len(c) > 10

def test_p20_synthetic_strategy_generator_blocks_live():
    s=synthetic_strategy_generator([{"edge_id":"x","asset":"WINFUT","timeframe":"H1"}])
    assert s[0]["status"]=="HYPOTHESIS_ONLY"
    assert s[0]["REAL_ORDERS"]=="FORBIDDEN"

def test_p20_deep_synthetic_lab():
    r=run()
    assert r["STATUS"]=="P20_DEEP_SYNTHETIC_LAB_IMPLEMENTED"
    assert r["MODULES_IMPLEMENTED"]==10
    assert r["LIVE"]=="FORBIDDEN"

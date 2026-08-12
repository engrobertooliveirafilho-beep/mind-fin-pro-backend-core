from app.p82_market_intelligence_domain.engine import run, classify_regime

def test_p82_classify_regime():
    r=classify_regime([1+i*0.01 for i in range(50)])
    assert r in ["BULL_TREND","TREND_HIGH_VOL","RANGE","VOLATILITY_EXPANSION"]

def test_p82_market_domain():
    r=run()
    assert r["STATUS"]=="P82_MARKET_INTELLIGENCE_DOMAIN_IMPLEMENTED"
    assert r["MODULES_IMPLEMENTED"]==24
    assert r["REAL_ORDERS"]=="FORBIDDEN"

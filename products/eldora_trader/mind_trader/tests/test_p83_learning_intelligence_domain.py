from app.p83_learning_intelligence_domain.engine import run, trade_outcome_learning

def test_p83_trade_outcome_learning():
    r=trade_outcome_learning([{"ticket":1,"symbol":"EURUSD","profit":-0.1}])
    assert r[0]["learning_signal"]=="MONITOR_EXIT_QUALITY"
    assert r[0]["REAL_ORDERS"]=="FORBIDDEN"

def test_p83_learning_domain():
    r=run()
    assert r["STATUS"]=="P83_LEARNING_INTELLIGENCE_DOMAIN_IMPLEMENTED"
    assert r["MODULES_IMPLEMENTED"]==10
    assert r["MT5_REAL"]=="FORBIDDEN"

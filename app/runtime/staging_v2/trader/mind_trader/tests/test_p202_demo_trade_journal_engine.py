from app.p202_demo_trade_journal_engine.engine import run

def test_p202():
    r=run()
    assert r["STATUS"]=="P202_DEMO_TRADE_JOURNAL_ENGINE_IMPLEMENTED"
    assert r["NEW_ORDER_SENT"] is False
    assert r["POSITION_CLOSE_SENT"] is False

from app.p121_200x_autonomous_demo_evidence_factory.engine import run

def test_p121_200_runtime():
    r=run()
    assert r["STATUS"]=="P121_200X_AUTONOMOUS_DEMO_EVIDENCE_FACTORY_IMPLEMENTED"
    assert r["MODULES_IMPLEMENTED"]==40
    assert r["NEW_ORDER_SENT"] is False
    assert r["REAL_ORDERS"]=="FORBIDDEN"

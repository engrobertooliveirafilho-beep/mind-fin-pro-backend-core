from app.p1513_p1514_web_strategy_arsenal.engine import web_registry, arsenal, run

def test_p1513_registry_has_hypotheses():
    r=web_registry()
    assert len(r)>0
    assert all(x["real_orders"]=="FORBIDDEN" for x in r)

def test_p1514_arsenal_assets():
    a=arsenal()
    assert any(x["asset"]=="WINFUT" for x in a)
    assert any(x["asset"]=="WDOFUT" for x in a)

def test_p1514_manifest():
    m=run()
    assert m["WEB_LEARNING"]=="ENABLED_AS_RESEARCH_ONLY"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True

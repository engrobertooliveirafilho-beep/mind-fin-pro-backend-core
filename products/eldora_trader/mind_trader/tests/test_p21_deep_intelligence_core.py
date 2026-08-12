from app.p21_deep_intelligence_core.engine import run, governance_layer, competition_brain

def test_p21_governance_layer_blocks_live():
    g=governance_layer()
    assert g["LIVE"]=="FORBIDDEN"
    assert g["REAL_ORDERS"]=="FORBIDDEN"

def test_p21_competition_brain():
    c=competition_brain([{"edge_id":"a","profit_factor":1},{"edge_id":"b","profit_factor":2}])
    assert c[0]["edge_id"]=="b"

def test_p21_deep_intelligence_core():
    r=run()
    assert r["STATUS"]=="P21_DEEP_INTELLIGENCE_CORE_IMPLEMENTED"
    assert r["MODULES_IMPLEMENTED"]==15
    assert r["REAL_ORDERS"]=="FORBIDDEN"

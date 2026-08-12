from app.p401_500x_promoted_edge_institutional_selection.engine import run

def test_p401_500_runtime():
    r=run()
    assert r["STATUS"]=="P401_500X_PROMOTED_EDGE_INSTITUTIONAL_SELECTION_IMPLEMENTED"
    assert r["REAL_ORDERS"]=="FORBIDDEN"
    assert r["FTMO_REAL"]=="FORBIDDEN"

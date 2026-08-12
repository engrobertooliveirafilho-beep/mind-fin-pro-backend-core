from app.p148_massive_ntsl_search_grid.engine import generate, code, run

def test_p148_code_has_orders():
    c=code(9,21)
    assert "BuyAtMarket" in c
    assert "SellShortAtMarket" in c

def test_p148_generate_many():
    rows=generate()
    assert len(rows) >= 100

def test_p148_manifest():
    m=run()
    assert m["STATUS"]=="P14.8_MASSIVE_NTSL_SEARCH_GRID_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True

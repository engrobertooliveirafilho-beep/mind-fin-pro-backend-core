from pathlib import Path
from app.p144_ntsl_strategy_factory.engine import ntsl_code, generate, run

def test_p144_generates_ntsl_code():
    c=ntsl_code("ema_cross")
    assert "begin" in c
    assert "BuyAtMarket" in c
    assert "SellShortAtMarket" in c

def test_p144_generate_catalog():
    rows=generate()
    assert len(rows)>0
    assert Path("strategies/ntsl_factory").exists()

def test_p144_manifest():
    m=run()
    assert m["STATUS"]=="P14.4_NTSL_STRATEGY_FACTORY_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True

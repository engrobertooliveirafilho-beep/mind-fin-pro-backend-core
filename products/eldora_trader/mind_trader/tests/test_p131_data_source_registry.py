from app.p13_data_source_registry.engine import build_registry, run, TARGET_ASSETS

def test_p131_registry_has_core_assets():
    assert "WIN" in TARGET_ASSETS
    assert "PETR4" in TARGET_ASSETS
    assert "AAPL" in TARGET_ASSETS
    assert "BTCUSD" in TARGET_ASSETS

def test_p131_registry_blocks_live():
    r=build_registry()
    assert len(r)>0
    assert all(x["live"]=="FORBIDDEN" for x in r)
    assert all(x["real_broker"]=="DISABLED" for x in r)

def test_p131_manifest():
    m=run()
    assert m["STATUS"]=="P13.1_DATA_SOURCE_REGISTRY_IMPLEMENTED"
    assert m["EXPORT_READY"] is True

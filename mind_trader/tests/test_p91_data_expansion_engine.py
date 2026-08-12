from app.p9_data_expansion_engine.engine import run, build_catalog, ASSET_UNIVERSE

def test_p91_catalog_includes_brazilian_stocks():
    assets=sum(ASSET_UNIVERSE.values(),[])
    assert "PETR4" in assets
    assert "VALE3" in assets

def test_p91_catalog_includes_international_stocks():
    assets=sum(ASSET_UNIVERSE.values(),[])
    assert "AAPL" in assets
    assert "NVDA" in assets

def test_p91_run_snapshot():
    s=run()["P9.1_STATE_SNAPSHOT"]
    assert s["STATUS"]=="P9.1_DATA_EXPANSION_ENGINE_REGISTERED"
    assert s["LIVE"]=="FORBIDDEN"
    assert s["EDGE"]=="NONE"
    assert s["EXPORT_READY"] is True

from app.p11_global_market_registry.engine import build_registry, coverage, run

def test_p113_contains_brazil_and_international_assets():
    symbols={x["symbol"] for x in build_registry()}
    assert "PETR4" in symbols
    assert "VALE3" in symbols
    assert "AAPL" in symbols
    assert "NVDA" in symbols
    assert "BTCUSD" in symbols

def test_p113_registry_blocks_live():
    r=build_registry()
    assert all(x["live"]=="FORBIDDEN" for x in r)
    assert all(x["real_broker"]=="DISABLED" for x in r)

def test_p113_coverage_report():
    r=build_registry()
    c=coverage(r)
    assert c["total_assets"] >= 15
    assert "stock" in c["by_asset_class"]

def test_p113_manifest():
    m=run()
    assert m["STATUS"]=="P11.3_GLOBAL_MARKET_REGISTRY_IMPLEMENTED"
    assert m["EXPORT_READY"] is True


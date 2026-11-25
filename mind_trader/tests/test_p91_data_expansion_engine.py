from app.p9_data_expansion_engine.engine import run, build_catalog, ASSET_UNIVERSE, TIMEFRAMES, SOURCES

def test_p91_catalog_includes_brazilian_stocks():
    assets=sum(ASSET_UNIVERSE.values(),[])
    assert "PETR4" in assets and "VALE3" in assets

def test_p91_catalog_includes_international_stocks():
    assets=sum(ASSET_UNIVERSE.values(),[])
    assert "AAPL" in assets and "NVDA" in assets

def test_p91_catalog_cardinality_and_unique_ids():
    catalog=build_catalog()
    assert len(catalog)==sum(map(len,ASSET_UNIVERSE.values()))*len(TIMEFRAMES)*len(SOURCES)
    assert len({x["dataset_id"] for x in catalog})==len(catalog)

def test_p91_slots_are_not_misreported_as_ingested_data():
    snapshot=run()["P9.1_STATE_SNAPSHOT"]
    assert snapshot["STATUS"]=="P9.1_CATALOG_ONLY_AWAITING_REAL_DATA"
    assert snapshot["DATASET_SLOTS_ONLY"] is True
    assert snapshot["INGESTION_EXECUTED"]==0
    assert snapshot["REAL_DATA_FILES"]==0
    assert snapshot["EXPORT_READY"] is False
    assert all(x["status"]=="REGISTERED_PENDING_DATA" for x in build_catalog())

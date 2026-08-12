from app.p10_real_dataset_registry_bridge.engine import bridge_dataset, bridge_many, run

def good():
    return {"dataset_id":"D1","asset":"WIN","timeframe":"M1","source":"MT5_CSV","audit":{"schema_ok":True,"rows":220,"timestamp_order":True,"duplicate_ratio":0,"missing_ratio":0,"ohlcv_consistency":True,"unique_closes":40,"volume_validity":True}}

def bad():
    return {"dataset_id":"D2","asset":"WIN","timeframe":"M1","source":"MT5_CSV","audit":{"schema_ok":False,"rows":10}}

def test_p103_bridge_certified_dataset_allows_backtest_only():
    r=bridge_dataset(good())
    assert r["backtest_allowed"] is True
    assert r["live"]=="FORBIDDEN"
    assert r["real_broker"]=="DISABLED"

def test_p103_bridge_rejects_bad_dataset():
    r=bridge_dataset(bad())
    assert r["backtest_allowed"] is False
    assert r["registry_status"]=="REGISTERED_REJECTED_OR_PENDING"

def test_p103_manifest():
    m=run()
    assert m["STATUS"]=="P10.3_REAL_DATASET_REGISTRY_BRIDGE_IMPLEMENTED"
    assert m["EXPORT_READY"] is True

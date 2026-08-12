from app.p10_certified_dataset_backtest_router.engine import route_to_backtest, run

def good():
    return {"dataset_id":"D1","asset":"WIN","timeframe":"M1","source":"MT5_CSV","audit":{"schema_ok":True,"rows":220,"timestamp_order":True,"duplicate_ratio":0,"missing_ratio":0,"ohlcv_consistency":True,"unique_closes":40,"volume_validity":True}}

def bad():
    return {"dataset_id":"D2","asset":"WIN","timeframe":"M1","source":"MT5_CSV","audit":{"schema_ok":False,"rows":10}}

def test_p104_routes_certified_dataset_to_backtest():
    r=route_to_backtest(good(),{"batch_start":0,"batch_size":1000})
    assert r["route_status"]=="BACKTEST_QUEUED"
    assert r["backtest_allowed"] is True
    assert r["live"]=="FORBIDDEN"

def test_p104_blocks_uncertified_dataset():
    r=route_to_backtest(bad(),{"batch_start":0,"batch_size":1000})
    assert r["route_status"]=="BLOCKED_DATASET_NOT_CERTIFIED"
    assert r["backtest_allowed"] is False

def test_p104_manifest():
    m=run()
    assert m["STATUS"]=="P10.4_CERTIFIED_DATASET_BACKTEST_ROUTER_IMPLEMENTED"
    assert m["EXPORT_READY"] is True

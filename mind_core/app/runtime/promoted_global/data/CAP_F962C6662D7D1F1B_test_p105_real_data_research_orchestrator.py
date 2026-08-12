from app.p10_real_data_research_orchestrator.engine import orchestrate, run

def good():
    return {"dataset_id":"D1","asset":"WIN","timeframe":"M1","source":"MT5_CSV","audit":{"schema_ok":True,"rows":220,"timestamp_order":True,"duplicate_ratio":0,"missing_ratio":0,"ohlcv_consistency":True,"unique_closes":40,"volume_validity":True}}

def bad():
    return {"dataset_id":"D2","asset":"WIN","timeframe":"M1","source":"MT5_CSV","audit":{"schema_ok":False,"rows":10}}

def test_p105_orchestrates_only_certified_routes():
    o=orchestrate([good(),bad()],[{"batch_start":0,"batch_size":1000}])
    assert o["routes_total"]==2
    assert o["routes_accepted"]==1
    assert o["routes_blocked"]==1
    assert o["live"]=="FORBIDDEN"

def test_p105_blocks_promotion():
    o=orchestrate([good()],[{"batch_start":0,"batch_size":1000}])
    assert o["promotion_allowed"] is False
    assert o["real_broker"]=="DISABLED"

def test_p105_manifest():
    m=run()
    assert m["STATUS"]=="P10.5_REAL_DATA_RESEARCH_ORCHESTRATOR_IMPLEMENTED"
    assert m["EXPORT_READY"] is True

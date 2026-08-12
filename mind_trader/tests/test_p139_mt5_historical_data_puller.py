from pathlib import Path
from app.p139_mt5_historical_data_puller.engine import dataset_id, normalize_rates, run, TIMEFRAMES

def test_p139_dataset_id():
    assert dataset_id("EURUSD","M1",500)

def test_p139_timeframes():
    assert "M1" in TIMEFRAMES
    assert "D1" in TIMEFRAMES

def test_p139_normalize_empty():
    assert normalize_rates(None)==[]

def test_p139_manifest():
    m=run()
    assert m["STATUS"]=="P13.9_MT5_HISTORICAL_DATA_PULLER_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True

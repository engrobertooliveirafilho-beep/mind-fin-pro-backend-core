from pathlib import Path
import pytest
from app.p139_mt5_historical_data_puller.engine import dataset_id, normalize_rates, run, TIMEFRAMES

def test_p139_dataset_id():
    assert dataset_id("EURUSD","M1",500)

def test_p139_timeframes():
    assert "M1" in TIMEFRAMES
    assert "D1" in TIMEFRAMES

def test_p139_normalize_empty():
    assert normalize_rates(None)==[]

def test_p139_manifest():
    with pytest.raises(PermissionError, match="ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED"):
        run()

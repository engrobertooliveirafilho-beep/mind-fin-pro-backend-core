from app.p68_real_market_daily_observer.engine import run, observe_dataset
from pathlib import Path

def test_p68_daily_observer_blocks_live():
    r=run(1)
    assert r["LIVE"]=="FORBIDDEN"
    assert r["REAL_ORDERS"]=="FORBIDDEN"
    assert r["validation_level"]=="REAL_DATASET_OBSERVATION"

def test_p68_observer_has_dataset_count():
    r=run(1)
    assert "datasets_observed" in r

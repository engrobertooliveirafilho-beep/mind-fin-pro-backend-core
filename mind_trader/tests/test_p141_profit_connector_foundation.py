from pathlib import Path
from app.p141_profit_connector_foundation.engine import run, discover_exports

def test_p141_discover_returns_list():
    assert isinstance(discover_exports(), list)

def test_p141_manifest():
    m=run()
    assert m["STATUS"]=="P14.1_PROFIT_CONNECTOR_FOUNDATION_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"

def test_p141_watch_dir_exists():
    run()
    assert Path("data/incoming/profit/watch").exists()

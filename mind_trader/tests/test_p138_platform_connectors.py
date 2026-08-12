from pathlib import Path
from app.p138_platform_connectors.engine import mt5_probe, profit_probe, ftmo_probe, run

def test_p138_mt5_probe_returns_status():
    s=mt5_probe()
    assert s["platform"]=="MT5"
    assert "available" in s

def test_p138_profit_bridge_creates_watch_dir():
    s=profit_probe()
    assert s["platform"]=="PROFIT"
    assert Path(s["watch_dir"]).exists()

def test_p138_ftmo_blocks_real_trading():
    s=ftmo_probe()
    assert s["platform"]=="FTMO"
    assert s["real_trading"]=="FORBIDDEN"

def test_p138_manifest():
    m=run()
    assert m["STATUS"]=="P13.8_PLATFORM_CONNECTORS_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True

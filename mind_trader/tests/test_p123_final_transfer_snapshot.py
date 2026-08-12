from pathlib import Path
from app.p12_final_transfer_snapshot.engine import build_snapshot

def test_p123_snapshot_certified():
    s=build_snapshot()["MIND_TRADER_TRANSFER_SNAPSHOT"]
    assert s["STATUS"]=="P12.3_FINAL_TRANSFER_SNAPSHOT_CERTIFIED"
    assert s["TESTS_LAST_CONFIRMED"]=="383 passed"
    assert s["EXPORT_READY"] is True

def test_p123_cloud_export_confirmed():
    s=build_snapshot()["MIND_TRADER_TRANSFER_SNAPSHOT"]
    assert s["CLOUD_EXPORT"]["confirmed"] is True
    assert s["CLOUD_EXPORT"]["status"]=="100%"

def test_p123_locks_preserved():
    s=build_snapshot()["MIND_TRADER_TRANSFER_SNAPSHOT"]
    assert s["LOCKS"]["LIVE"]=="FORBIDDEN"
    assert s["LOCKS"]["REAL_BROKER"]=="DISABLED"
    assert s["RESEARCH_STATE"]["EDGE"]=="NOT_PROVEN"

def test_p123_files_written():
    build_snapshot()
    assert Path("reports/P12.3_FINAL_TRANSFER_SNAPSHOT/MIND_TRADER_TRANSFER_SNAPSHOT.json").exists()


from pathlib import Path
from mind_trader.app.audits.transfer_snapshot import build_transfer_snapshot, save_transfer_snapshot

def test_transfer_snapshot_structure():
    s=build_transfer_snapshot(148)
    assert s["snapshot"]=="P8.55_TRANSFER_SNAPSHOT"
    assert s["tests_passed"]==148
    assert s["production"]=="BLOCKED"
    assert s["live"]=="FORBIDDEN"
    assert s["edge_claim"]=="NONE"
    assert len(s["snapshot_hash"])==64

def test_transfer_snapshot_modules_range():
    s=build_transfer_snapshot(148)
    assert "P8.26" in s["modules_validated"]
    assert "P8.54" in s["modules_validated"]

def test_save_transfer_snapshot(tmp_path):
    s=save_transfer_snapshot(str(tmp_path/"transfer.json"),148)
    assert Path(tmp_path/"transfer.json").exists()
    assert s["next_recommended_layer"]=="P8.56_CLOUD_EXPORT_AND_REMOTE_STORAGE"

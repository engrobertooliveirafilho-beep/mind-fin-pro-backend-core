from pathlib import Path
from mind_trader.app.audits.cloud_export import build_export_manifest, export_to_directory

def test_manifest_builds():
    r=build_export_manifest(tests_passed=151)
    assert r["manifest"]=="P8.56_CLOUD_EXPORT_MANIFEST"
    assert r["tests_passed"]==151
    assert len(r["manifest_hash"])==64

def test_export_blocks_without_destination():
    r=export_to_directory("",tests_passed=151)
    assert r["decision"]=="BLOCKED_NO_REMOTE_DESTINATION"

def test_export_to_directory_real_copy(tmp_path):
    r=export_to_directory(str(tmp_path/"remote"),tests_passed=151)
    assert r["decision"]=="EXPORT_COMPLETED"
    assert Path(r["manifest_path"]).exists()
    assert r["production"]=="BLOCKED"
    assert r["edge_claim"]=="NONE"

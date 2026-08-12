from pathlib import Path
from mind_trader.app.audits.cloud_export import export_to_directory
from mind_trader.app.audits.export_verifier import verify_export_directory

def test_verify_missing_manifest_fails(tmp_path):
    r=verify_export_directory(str(tmp_path/"empty"))
    assert r["decision"]=="EXPORT_VERIFY_FAILED"

def test_verify_export_ok(tmp_path):
    dest=tmp_path/"remote"
    export_to_directory(str(dest),tests_passed=154)
    r=verify_export_directory(str(dest))
    assert r["decision"]=="EXPORT_VERIFY_OK"
    assert r["production"]=="BLOCKED"

def test_verify_detects_tamper(tmp_path):
    dest=tmp_path/"remote"
    export_to_directory(str(dest),tests_passed=154)
    files=[p for p in dest.glob("*.json") if p.name!="P8.56_cloud_export_manifest.json"]
    files[0].write_text("tampered",encoding="utf-8")
    r=verify_export_directory(str(dest))
    assert r["decision"]=="EXPORT_VERIFY_FAILED"
    assert r["failures"]

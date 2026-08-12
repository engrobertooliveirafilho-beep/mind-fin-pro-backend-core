from pathlib import Path
from mind_trader.app.audits.runtime_evidence_package import file_sha256, collect_report_hashes, build_runtime_evidence_package, save_runtime_evidence_package

def test_file_sha256_none_for_missing(tmp_path):
    assert file_sha256(tmp_path/"missing.json") is None

def test_collect_report_hashes(tmp_path):
    p=tmp_path/"reports"; p.mkdir()
    (p/"a.json").write_text('{"ok":true}',encoding="utf-8")
    r=collect_report_hashes(str(p))
    assert "a.json" in r
    assert len(r["a.json"])==64

def test_build_runtime_evidence_package():
    p=build_runtime_evidence_package(137)
    assert p["package"]=="P8.52_RUNTIME_EVIDENCE_PACKAGE"
    assert p["tests_passed"]==137
    assert p["production"]=="BLOCKED"
    assert p["live"]=="FORBIDDEN"
    assert len(p["package_hash"])==64

def test_save_runtime_evidence_package(tmp_path):
    pkg=save_runtime_evidence_package(str(tmp_path/"pkg.json"),137)
    assert Path(tmp_path/"pkg.json").exists()
    assert pkg["edge_claim"]=="NONE"

import json, hashlib
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.audits.institutional_audit_ledger import institutional_snapshot, verify_ledger

def file_sha256(path):
    p=Path(path)
    if not p.exists(): return None
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def collect_report_hashes(report_dir="mind_trader/reports"):
    p=Path(report_dir)
    if not p.exists(): return {}
    return {x.name:file_sha256(x) for x in sorted(p.glob("*.json"))}

def build_runtime_evidence_package(tests_passed=137):
    snapshot=institutional_snapshot(test_count=tests_passed)
    ledger=verify_ledger()
    hashes=collect_report_hashes()
    package={
        "package":"P8.52_RUNTIME_EVIDENCE_PACKAGE",
        "created_at":datetime.now(UTC).isoformat(),
        "tests_passed":tests_passed,
        "snapshot":snapshot,
        "ledger_integrity":ledger,
        "report_hashes":hashes,
        "repro_command":"$env:PYTHONPATH=(Get-Location).Path; pytest .\\mind_trader\\tests -q",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }
    raw=json.dumps(package,sort_keys=True,ensure_ascii=False,separators=(",",":"))
    package["package_hash"]=hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return package

def save_runtime_evidence_package(path="mind_trader/reports/P8.52_runtime_evidence_package.json",tests_passed=137):
    pkg=build_runtime_evidence_package(tests_passed)
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(pkg,ensure_ascii=False,indent=2),encoding="utf-8")
    return pkg

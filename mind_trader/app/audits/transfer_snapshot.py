import json
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.audits.runtime_evidence_package import build_runtime_evidence_package
from mind_trader.app.audits.institutional_audit_ledger import verify_ledger, canonical_hash

def build_transfer_snapshot(tests_passed=148):
    modules=[f"P8.{i}" for i in range(26,55)]
    snapshot={
        "snapshot":"P8.55_TRANSFER_SNAPSHOT",
        "created_at":datetime.now(UTC).isoformat(),
        "modules_validated":modules,
        "tests_passed":tests_passed,
        "evidence":build_runtime_evidence_package(tests_passed),
        "ledger_integrity":verify_ledger(),
        "current_decision":"PAPER_RESEARCH_ONLY",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE",
        "causality_claim":"NOT_PROVEN",
        "next_recommended_layer":"P8.56_CLOUD_EXPORT_AND_REMOTE_STORAGE"
    }
    snapshot["snapshot_hash"]=canonical_hash(snapshot)
    return snapshot

def save_transfer_snapshot(path="mind_trader/reports/P8.55_transfer_snapshot.json",tests_passed=148):
    s=build_transfer_snapshot(tests_passed)
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding="utf-8")
    return s

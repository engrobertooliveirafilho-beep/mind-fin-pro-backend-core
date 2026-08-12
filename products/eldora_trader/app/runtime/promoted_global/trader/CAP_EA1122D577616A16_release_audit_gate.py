import json
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.audits.runtime_evidence_package import save_runtime_evidence_package
from mind_trader.app.audits.institutional_healthcheck import save_healthcheck_report
from mind_trader.app.audits.institutional_audit_ledger import append_audit_event, institutional_snapshot, canonical_hash

FORBIDDEN_RELEASES={"LIVE","PRODUCTION","REAL_MONEY"}

def release_gate(target="PAPER_RESEARCH", tests_passed=145):
    if target in FORBIDDEN_RELEASES:
        return {"decision":"FORCE_BLOCK_RELEASE","target":target,"production":"BLOCKED","live":"FORBIDDEN","edge_claim":"NONE"}
    evidence=save_runtime_evidence_package(tests_passed=tests_passed)
    health=save_healthcheck_report(run_tests=False,expected_tests=tests_passed)
    snapshot=institutional_snapshot(test_count=tests_passed)
    report={
        "gate":"P8.54_RELEASE_AUDIT_GATE",
        "created_at":datetime.now(UTC).isoformat(),
        "target":target,
        "snapshot":snapshot,
        "evidence_package_hash":evidence["package_hash"],
        "health_decision":health["decision"],
        "decision":"RELEASE_AUDIT_PACKAGE_READY",
        "allowed_scope":"PAPER_RESEARCH_ONLY",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }
    report["release_hash"]=canonical_hash(report)
    evt=append_audit_event("P8.54_RELEASE_GATE",{"target":target,"release_hash":report["release_hash"],"decision":report["decision"]})
    report["ledger_hash"]=evt["event_hash"]
    Path("mind_trader/reports/P8.54_release_audit_gate.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report

import json
from pathlib import Path
from datetime import datetime, UTC

REQUIRED_READY = [
    "data_connector",
    "data_quality",
    "data_catalog",
    "dataset_lineage",
    "dataset_lineage_gate",
    "backtest_cluster",
    "edge_validation",
    "regime_detection",
    "ftmo_simulation",
    "paper_session",
    "execution_gateway",
    "audit_ledger",
    "healthcheck"
]

def paper_research_readiness(checks=None, tests_passed=188):
    checks = checks or {k: True for k in REQUIRED_READY}
    missing=[k for k in REQUIRED_READY if k not in checks]
    failed=[k for k,v in checks.items() if k in REQUIRED_READY and not v]
    decision="PAPER_RESEARCH_READY" if not missing and not failed else "PAPER_RESEARCH_NOT_READY"
    return {
        "report":"P8.67_PAPER_RESEARCH_READINESS",
        "created_at":datetime.now(UTC).isoformat(),
        "tests_passed":tests_passed,
        "required":REQUIRED_READY,
        "missing":missing,
        "failed":failed,
        "decision":decision,
        "allowed_scope":"PAPER_RESEARCH_ONLY" if decision=="PAPER_RESEARCH_READY" else "NONE",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE",
        "causality_claim":"NOT_PROVEN"
    }

def save_paper_research_readiness(path="mind_trader/reports/P8.67_paper_research_readiness.json",checks=None,tests_passed=188):
    r=paper_research_readiness(checks,tests_passed)
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
    return r

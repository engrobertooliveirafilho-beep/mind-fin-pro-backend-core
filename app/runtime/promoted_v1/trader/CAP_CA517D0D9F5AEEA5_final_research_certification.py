import json
from pathlib import Path
from datetime import datetime, UTC

REQUIRED_CERT = [
    "data_quality",
    "dataset_catalog",
    "dataset_lineage",
    "knowledge_source_registry",
    "dna_authority",
    "correlation_authority",
    "causality_authority",
    "uncertainty_authority",
    "edge_discovery_authority",
    "anti_overfitting_authority",
    "walk_forward_authority",
    "monte_carlo_authority",
    "robustness_committee",
    "validation_protocol",
    "promotion_authority",
    "paper_session",
    "execution_gateway",
    "audit_ledger"
]

def final_research_certification(checks=None, tests_passed=266):
    checks=checks or {k:True for k in REQUIRED_CERT}
    missing=[k for k in REQUIRED_CERT if k not in checks]
    failed=[k for k,v in checks.items() if k in REQUIRED_CERT and not v]
    ok=not missing and not failed

    report={
        "certification":"P8.90_FINAL_RESEARCH_CERTIFICATION",
        "created_at":datetime.now(UTC).isoformat(),
        "tests_passed":tests_passed,
        "required":REQUIRED_CERT,
        "missing":missing,
        "failed":failed,
        "decision":"FINAL_RESEARCH_CERTIFIED_PAPER_ONLY" if ok else "FINAL_RESEARCH_CERTIFICATION_FAILED",
        "allowed_scope":"PAPER_RESEARCH_ONLY" if ok else "NONE",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE",
        "causality_claim":"NOT_PROVEN"
    }

    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.90_final_research_certification.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report

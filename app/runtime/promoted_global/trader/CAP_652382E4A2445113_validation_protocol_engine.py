import json
from pathlib import Path
from datetime import datetime, UTC

REQUIRED_EVIDENCE = [
    "edge_validation",
    "walk_forward",
    "monte_carlo",
    "stress_test",
    "degradation_test",
    "regime_stability",
    "cross_asset_stability",
    "risk_of_ruin",
    "ftmo_simulation",
    "adversarial_validation",
    "digital_twin_replay",
    "robustness_committee"
]

FORBIDDEN_APPROVALS = {"LIVE_APPROVED","PRODUCTION_APPROVED","REAL_MONEY_APPROVED"}

def force_block_forbidden_decision(decision):
    if decision in FORBIDDEN_APPROVALS:
        return {"decision":"FORCE_BLOCK","reason":"REAL_EXECUTION_APPROVAL_FORBIDDEN","production":"BLOCKED","edge_claim":"NONE"}
    return {"decision":decision,"production":"BLOCKED"}

def _item_ok(item):
    if isinstance(item,bool):
        return item
    if isinstance(item,dict):
        return bool(
            item.get("passed") is True or
            item.get("ok") is True or
            item.get("decision") in [
                "PASS",
                "ALLOW",
                "PAPER_TRADING_CANDIDATE",
                "PAPER_TRADING_APPROVED",
                "ROBUSTNESS_PASS_PAPER_CANDIDATE"
            ]
        )
    return False

def validate_evidence_package(package):
    missing=[k for k in REQUIRED_EVIDENCE if k not in package]
    if missing:
        return {
            "decision":"INCOMPLETE_EVIDENCE",
            "missing":missing,
            "production":"BLOCKED",
            "edge_claim":"NONE"
        }

    failed=[k for k in REQUIRED_EVIDENCE if not _item_ok(package[k])]

    if failed:
        return {
            "decision":"REJECTED_EDGE",
            "failed":failed,
            "production":"BLOCKED",
            "edge_claim":"NONE"
        }

    return {
        "decision":"PAPER_TRADING_APPROVED",
        "approved_scope":"PAPER_ONLY",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"PAPER_RESEARCH_CANDIDATE_ONLY"
    }

def classify_validation_package(package):
    result=validate_evidence_package(package)
    return force_block_forbidden_decision(result["decision"]) if result["decision"] in FORBIDDEN_APPROVALS else result

def validation_committee_report(genome_id, package):
    result=classify_validation_package(package)
    return {
        "genome_id":genome_id,
        "committee":"P8.84_VALIDATION_PROTOCOL_WITH_ROBUSTNESS",
        "evaluated_at":datetime.now(UTC).isoformat(),
        "required_evidence":REQUIRED_EVIDENCE,
        "result":result,
        "production":"BLOCKED",
        "live":"FORBIDDEN"
    }

def save_validation_committee_report(report,path="mind_trader/reports/P8.84_validation_committee_robustness.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return path

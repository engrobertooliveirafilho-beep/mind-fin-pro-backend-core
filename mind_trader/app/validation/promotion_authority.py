import json
from pathlib import Path
from datetime import datetime, UTC

FORBIDDEN_TARGETS={"LIVE","PRODUCTION","REAL_MONEY","FTMO_REAL"}

def promotion_authority(genome_id, validation_result, requested_target="PAPER"):
    if requested_target in FORBIDDEN_TARGETS:
        decision="FORCE_BLOCK_PROMOTION"
        allowed=False
        reason="REAL_OR_LIVE_PROMOTION_FORBIDDEN"
    elif validation_result.get("decision")=="PAPER_TRADING_APPROVED":
        decision="PROMOTE_TO_PAPER_RESEARCH_ONLY"
        allowed=True
        reason="VALIDATED_FOR_PAPER_SCOPE_ONLY"
    else:
        decision="PROMOTION_REJECTED"
        allowed=False
        reason="VALIDATION_NOT_APPROVED"

    report={
        "authority":"P8.85_PROMOTION_AUTHORITY",
        "created_at":datetime.now(UTC).isoformat(),
        "genome_id":genome_id,
        "requested_target":requested_target,
        "allowed":allowed,
        "decision":decision,
        "reason":reason,
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE" if not allowed else "PAPER_RESEARCH_CANDIDATE_ONLY"
    }

    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.85_promotion_authority.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report

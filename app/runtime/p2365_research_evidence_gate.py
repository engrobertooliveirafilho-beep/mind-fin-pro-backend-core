"""P2365 reconciliation: in-sample context ranking is research, never promotion."""
from __future__ import annotations
import math


def assess_p2365_context(summary: dict, *, chronological_oos_verified: bool = False,
                         independent_lineage_verified: bool = False) -> dict:
    result = {"approved": False, "decision": "BLOCK_OOS_UNVERIFIED",
              "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN",
              "ftmo_real": "FORBIDDEN"}
    if not isinstance(summary, dict):
        return result
    if chronological_oos_verified is not True or independent_lineage_verified is not True:
        return result
    try:
        rows = summary["source_rows"]
        contexts = summary["contexts_ranked"]
        promoted = summary["promoted_contexts"]
        if any(type(v) is not int or v < 0 for v in (rows, contexts, promoted)):
            return result
        if rows == 0 or contexts == 0 or promoted > contexts:
            return result
        if summary.get("mode") != "PAPER_ONLY":
            return result
        if summary.get("real_orders") != "FORBIDDEN" or summary.get("ftmo_real") != "FORBIDDEN":
            return result
        if summary.get("symbol") != "DE40" or summary.get("source_timeframe") != "M5":
            return result
        if promoted != 0:
            result["decision"] = "BLOCK_HISTORICAL_PROMOTION_REQUIRES_REPLAY"
            return result
    except (KeyError, TypeError, ValueError, OverflowError):
        return result
    result["decision"] = "RESEARCH_EVIDENCE_ACCEPTED_NO_PROMOTION"
    return result

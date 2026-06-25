from __future__ import annotations

from app.runtime.p2353_signal_precheck_institutional_score import institutional_signal_score

def precheck_before_mt5_emit(signal: dict, context: dict) -> dict:
    score = institutional_signal_score(signal, context)
    allowed = score["decision"] in {"APPROVE_SMALL", "APPROVE", "PRIORITY"}

    return {
        "emit_allowed": allowed,
        "decision": score["decision"],
        "institutional_score": score["institutional_score"],
        "lot_multiplier": score["lot_multiplier"] if allowed else 0.0,
        "reasons": score["reasons"],
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

def health() -> dict:
    return {
        "status": "OK",
        "engine": "P2354_SIGNAL_EMISSION_BLOCKER",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

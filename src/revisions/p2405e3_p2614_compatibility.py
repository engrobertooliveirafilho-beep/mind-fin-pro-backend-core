"""P2405E3 -> P2614 offline compatibility audit. Never promotes candidates."""
import hashlib

PAPER_DIRECTIONS = frozenset(("BUY_PAPER", "SELL_PAPER"))
P2614_FAMILIES = frozenset(("LIQUIDITY", "FALSE_BREAKOUT", "VOLATILITY", "ATR", "MOMENTUM", "TREND", "REVERSAL", "RANGE", "BREAKOUT", "CANDLE", "MICROSTRUCTURE"))
P2614_RISK_MODELS = frozenset(("FIXED_1R", "ATR_STOP", "TRAILING", "LOSS_GUARD", "COOLDOWN", "TIME_STOP", "PARTIAL_TP"))
REQUIRED = ("edge_id", "family", "pattern", "session", "regime", "timeframe", "direction", "risk_model", "filter")

def audit_candidate(candidate):
    reasons = []
    if not isinstance(candidate, dict):
        return {"compatible": False, "runtime_allowed": False, "reasons": ["INVALID_RECORD"]}
    for field in REQUIRED:
        if not isinstance(candidate.get(field), str) or not candidate[field].strip():
            reasons.append("MISSING_" + field.upper())
    if reasons:
        return {"compatible": False, "runtime_allowed": False, "reasons": reasons}
    if candidate.get("mode") != "PAPER_ONLY" or candidate.get("real_orders") != "FORBIDDEN" or candidate.get("ftmo_real") != "FORBIDDEN" or candidate.get("real_execution_allowed") is not False:
        reasons.append("PAPER_GOVERNANCE_FAILURE")
    if candidate["direction"] not in PAPER_DIRECTIONS: reasons.append("INVALID_DIRECTION")
    if candidate["family"] not in P2614_FAMILIES: reasons.append("UNSUPPORTED_FAMILY")
    if candidate["risk_model"] not in P2614_RISK_MODELS: reasons.append("UNSUPPORTED_RISK_MODEL")
    # P2614 signal logic lacks P2405E3 pattern/filter semantics: never silently ignore them.
    if candidate["pattern"] != "NO_PATTERN" or candidate["filter"] != "NO_FILTER":
        reasons.append("UNIMPLEMENTED_PATTERN_OR_FILTER")
    return {"compatible": not reasons, "runtime_allowed": False, "reasons": reasons}

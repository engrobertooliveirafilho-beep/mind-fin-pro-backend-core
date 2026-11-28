from __future__ import annotations

from app.runtime.p2353_signal_precheck_institutional_score import institutional_signal_score


def _conflicting_directions(signal: dict, context: dict) -> bool:
    """Fail closed when same-symbol/candle candidate directions disagree."""
    candidates = context.get("candidate_signals")
    if candidates is None:
        return True  # Missing batch evidence must block.
    if not isinstance(candidates, (list, tuple)) or not candidates:
        return True
    symbol = signal.get("symbol")
    timeframe = signal.get("timeframe") or context.get("timeframe")
    candle = signal.get("candle_key") or context.get("candle_key")
    if not symbol or not timeframe or not candle:
        return True
    directions = set()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            return True
        if (candidate.get("symbol") == symbol
                and (candidate.get("timeframe") or context.get("timeframe")) == timeframe
                and (candidate.get("candle_key") or context.get("candle_key")) == candle):
            side = str(candidate.get("side") or candidate.get("action") or "").upper()
            if side not in {"BUY", "SELL"}:
                return True
            directions.add(side)
    current_side = str(signal.get("side") or signal.get("action") or "").upper()
    if current_side not in {"BUY", "SELL"}:
        return True
    if current_side not in directions:
        return True
    return len(directions) > 1


def precheck_before_mt5_emit(signal: dict, context: dict) -> dict:
    if _conflicting_directions(signal, context):
        return {
            "emit_allowed": False,
            "decision": "BLOCK_CONFLICTING_DIRECTIONS_SAME_CANDLE",
            "institutional_score": 0,
            "lot_multiplier": 0.0,
            "reasons": ["CONFLICTING_BUY_SELL_SAME_SYMBOL_TIMEFRAME_CANDLE"],
            "mode": "PAPER_ONLY",
            "real_orders": "FORBIDDEN",
            "ftmo_real": "FORBIDDEN",
        }
    score = institutional_signal_score(signal, context)
    vetoes = {"REGIME_BLOCK", "EARLY_MOVE_BLOCK", "WAIT_CONFIRMATION",
              "POST_LOSS_GATE_BLOCK", "CORRELATION_RISK", "GOVERNANCE_BLOCK",
              "PAYOFF_BELOW_3X"}
    allowed = (score["decision"] in {"APPROVE_SMALL", "APPROVE", "PRIORITY"}
               and not vetoes.intersection(score["reasons"])
               and context.get("mode") == "PAPER_ONLY"
               and context.get("real_orders") == "FORBIDDEN"
               and context.get("ftmo_real") == "FORBIDDEN")

    return {
        "emit_allowed": allowed,
        "decision": score["decision"] if allowed else "BLOCK",
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

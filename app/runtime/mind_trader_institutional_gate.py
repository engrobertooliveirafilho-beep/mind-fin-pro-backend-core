from __future__ import annotations

from datetime import datetime
from app.runtime.p2354_signal_emission_blocker import precheck_before_mt5_emit


def _block(reason):
    return {"ok": False, "status": "BLOCK", "emit_allowed": False,
            "lot_multiplier": 0.0, "reasons": [reason],
            "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN",
            "ftmo_real": "FORBIDDEN"}


def _timestamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be ISO-8601")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None:
        raise ValueError("timezone required")
    return parsed


def run_gate(payload=None):
    if not isinstance(payload, dict):
        return _block("INVALID_PAYLOAD")
    signal, context = payload.get("signal"), payload.get("context")
    if not isinstance(signal, dict) or not isinstance(context, dict):
        return _block("MISSING_SIGNAL_CONTEXT")
    if (context.get("mode") != "PAPER_ONLY"
            or context.get("real_orders") != "FORBIDDEN"
            or context.get("ftmo_real") != "FORBIDDEN"):
        return _block("UNSAFE_MODE")
    try:
        times = context["closed_candle_times"]
        if not isinstance(times, (list, tuple)) or not times:
            return _block("MISSING_CANDLE_HISTORY")
        parsed = [_timestamp(t) for t in times]
        if any(b <= a for a, b in zip(parsed, parsed[1:])):
            return _block("NONMONOTONIC_CANDLE_TIME")
        decision_time = _timestamp(context["decision_time"])
        candle_time = _timestamp(signal["candle_key"])
        if candle_time != parsed[-1] or candle_time > decision_time:
            return _block("INVALID_EVENT_CHRONOLOGY")
        candidates = context["candidate_signals"]
        if not isinstance(candidates, (list, tuple)) or not candidates:
            return _block("MISSING_CANDIDATE_BATCH")
        for candidate in candidates:
            if not isinstance(candidate, dict):
                return _block("INVALID_CANDIDATE")
            if _timestamp(candidate["candle_key"]) != candle_time:
                return _block("UNSYNCHRONIZED_CANDIDATE")
            if _timestamp(candidate["observed_at"]) > decision_time:
                return _block("FUTURE_CANDIDATE")
        if signal not in candidates:
            return _block("SIGNAL_NOT_IN_BATCH")
        result = precheck_before_mt5_emit(signal, context)
        if not isinstance(result, dict):
            return _block("INVALID_ENGINE_RESULT")
        if (result.get("emit_allowed") is not True
                or result.get("mode") != "PAPER_ONLY"
                or result.get("real_orders") != "FORBIDDEN"
                or result.get("ftmo_real") != "FORBIDDEN"):
            return _block("INSTITUTIONAL_GATE_REJECTED") | {"engine_result": result}
        return {"ok": True, "status": "PAPER_PRECHECK_APPROVED",
                "emit_allowed": False, "paper_precheck_allowed": True,
                "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN",
                "ftmo_real": "FORBIDDEN", "engine_result": result}
    except Exception:
        return _block("INVALID_CHRONOLOGY_OR_ENGINE_ERROR")


def health():
    return {"ok": False, "status": "implemented_unverified",
            "module": "mind_trader_institutional_gate", "mode": "paper_only"}

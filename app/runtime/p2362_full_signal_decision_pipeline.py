from __future__ import annotations

from app.runtime.p2356_context_regime_edge_engine import classify_context_edge
from app.runtime.p2354_signal_emission_blocker import precheck_before_mt5_emit
from app.runtime.p2361_dynamic_position_sizing_engine import dynamic_paper_lot
from app.runtime.p2366_institutional_targeting_engine import institutional_targets

def decide_signal(signal: dict, context: dict) -> dict:
    context_edge = classify_context_edge(context)
    target = institutional_targets({
        "side": signal.get("side"),
        "entry": signal.get("entry", context.get("entry")),
        "stop": signal.get("stop", context.get("stop")),
        "swing_high": context.get("swing_high") or context.get("entry") or signal.get("entry"),
        "swing_low": context.get("swing_low") or context.get("entry") or signal.get("entry"),
        "atr": context.get("atr") or 0,
        "session_high": context.get("session_high") or context.get("swing_high") or context.get("entry") or signal.get("entry"),
        "session_low": context.get("session_low") or context.get("swing_low") or context.get("entry") or signal.get("entry"),
        "liquidity_high": context.get("liquidity_high") or context.get("session_high") or context.get("swing_high") or context.get("entry") or signal.get("entry"),
        "liquidity_low": context.get("liquidity_low") or context.get("session_low") or context.get("swing_low") or context.get("entry") or signal.get("entry"),
        "vwap": context.get("vwap") or context.get("entry") or signal.get("entry"),
        "round_number": context.get("round_number") or context.get("entry") or signal.get("entry"),
    })

    if not target.get("approved", False):
        return {
            "symbol": signal.get("symbol"),
            "side": signal.get("side"),
            "strategy": signal.get("strategy"),
            "context_edge": context_edge,
            "targeting": target,
            "final_decision": "BLOCK_SIGNAL_TARGET_BELOW_2R",
            "paper_lot": 0.0,
            "mode": "PAPER_ONLY",
            "real_orders": "FORBIDDEN",
            "ftmo_real": "FORBIDDEN",
        }

    signal = dict(signal)
    signal["expected_payoff"] = max(float(signal.get("expected_payoff", 0)), float(target.get("rr", 0)))

    precheck = precheck_before_mt5_emit(signal, context)

    sizing = dynamic_paper_lot({
        "base_lot": signal.get("base_lot", 0.01),
        "institutional_score": precheck.get("institutional_score", 0),
        "expected_payoff": signal.get("expected_payoff", 0),
        "current_drawdown": context.get("current_drawdown", 0),
        "correlation_ok": context.get("correlation_ok", True),
        "last_trade_loss": context.get("last_loss", False),
        "rebuild_after_profit": context.get("rebuild_after_profit", False),
    })

    final_emit = bool(precheck["emit_allowed"]) and float(sizing["recommended_paper_lot"]) > 0

    return {
        "symbol": signal.get("symbol"),
        "side": signal.get("side"),
        "strategy": signal.get("strategy"),
        "context_edge": context_edge,
        "targeting": target,
        "precheck": precheck,
        "sizing": sizing,
        "final_decision": "EMIT_TO_MT5_PAPER" if final_emit else "BLOCK_SIGNAL",
        "paper_lot": sizing["recommended_paper_lot"] if final_emit else 0.0,
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

def health() -> dict:
    return {
        "status": "OK",
        "engine": "P2362_FULL_SIGNAL_DECISION_PIPELINE_WITH_P2366_TARGETING",
        "target_min_rr": 2.0,
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }


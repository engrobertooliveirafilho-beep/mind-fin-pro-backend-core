from __future__ import annotations

from app.runtime.p2356_context_regime_edge_engine import classify_context_edge
from app.runtime.p2354_signal_emission_blocker import precheck_before_mt5_emit
from app.runtime.p2361_dynamic_position_sizing_engine import dynamic_paper_lot
from app.runtime.p2366_institutional_targeting_engine import institutional_targets

def decide_signal(signal: dict, context: dict) -> dict:
    # Invalid envelopes cannot reach context classification or targeting.
    if not isinstance(signal, dict) or not isinstance(context, dict):
        return {
            "final_decision": "BLOCK_INVALID_ENVELOPE", "paper_lot": 0.0,
            "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN",
        }
    context_edge = classify_context_edge(context)
    def fallback(*values):
        return next((v for v in values if v is not None), None)

    target = institutional_targets({
        "side": signal.get("side"),
        "entry": fallback(signal.get("entry"), context.get("entry")),
        "stop": fallback(signal.get("stop"), context.get("stop")),
        "swing_high": fallback(context.get("swing_high"), context.get("entry"), signal.get("entry")),
        "swing_low": fallback(context.get("swing_low"), context.get("entry"), signal.get("entry")),
        "atr": fallback(context.get("atr"), 0),
        "session_high": fallback(context.get("session_high"), context.get("swing_high"), context.get("entry"), signal.get("entry")),
        "session_low": fallback(context.get("session_low"), context.get("swing_low"), context.get("entry"), signal.get("entry")),
        "liquidity_high": fallback(context.get("liquidity_high"), context.get("session_high"), context.get("swing_high"), context.get("entry"), signal.get("entry")),
        "liquidity_low": fallback(context.get("liquidity_low"), context.get("session_low"), context.get("swing_low"), context.get("entry"), signal.get("entry")),
        "vwap": fallback(context.get("vwap"), context.get("entry"), signal.get("entry")),
        "round_number": fallback(context.get("round_number"), context.get("entry"), signal.get("entry")),
    })

    if not target.get("approved", False):
        return {
            "symbol": signal.get("symbol"),
            "side": signal.get("side"),
            "strategy": signal.get("strategy"),
            "context_edge": context_edge,
            "targeting": target,
            "final_decision": ("BLOCK_SIGNAL_TARGET_BELOW_2R" if target.get("decision") == "BLOCK_TARGET_BELOW_2R" else "BLOCK_SIGNAL_INVALID_TARGET"),
            "paper_lot": 0.0,
            "mode": "PAPER_ONLY",
            "real_orders": "FORBIDDEN",
            "ftmo_real": "FORBIDDEN",
        }

    # The target is a geometric opportunity, not independently verified expectancy.
    # Never inflate an explicit strategy expectancy using the target RR.
    import math
    signal = dict(signal)
    try:
        observed_payoff = float(signal.get("expected_payoff", 0))
    except (TypeError, ValueError, OverflowError):
        observed_payoff = float("nan")
    if isinstance(signal.get("expected_payoff"), bool) or not math.isfinite(observed_payoff) or observed_payoff < 0:
        return {
            "symbol": signal.get("symbol"), "side": signal.get("side"),
            "strategy": signal.get("strategy"), "context_edge": context_edge,
            "targeting": target, "final_decision": "BLOCK_INVALID_EXPECTANCY",
            "paper_lot": 0.0, "mode": "PAPER_ONLY",
            "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN",
        }
    signal["expected_payoff"] = observed_payoff

    precheck = precheck_before_mt5_emit(signal, context)
    if not isinstance(precheck, dict) or precheck.get("emit_allowed") is not True:
        return {
            "symbol": signal.get("symbol"), "side": signal.get("side"),
            "strategy": signal.get("strategy"), "context_edge": context_edge,
            "targeting": target,
            "precheck": precheck if isinstance(precheck, dict) else None,
            "final_decision": "BLOCK_PRECHECK",
            "paper_lot": 0.0, "mode": "PAPER_ONLY",
            "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN",
        }

    sizing = dynamic_paper_lot({
        "base_lot": signal.get("base_lot", 0.01),
        "institutional_score": precheck.get("institutional_score", 0),
        "expected_payoff": signal.get("expected_payoff", 0),
        "current_drawdown": context.get("current_drawdown", 0),
        "correlation_ok": context.get("correlation_ok") is True,
        "last_trade_loss": context.get("last_loss", False),
        "rebuild_after_profit": context.get("rebuild_after_profit", False),
    })

    # Untrusted sizing outputs must never become an emission authorization.
    try:
        raw_lot = sizing.get("recommended_paper_lot") if isinstance(sizing, dict) else None
        paper_lot = float(raw_lot)
    except (TypeError, ValueError, OverflowError):
        paper_lot = 0.0
    if isinstance(raw_lot, bool) or not math.isfinite(paper_lot) or paper_lot <= 0:
        paper_lot = 0.0
    final_emit = isinstance(precheck, dict) and precheck.get("emit_allowed") is True and paper_lot > 0

    return {
        "symbol": signal.get("symbol"),
        "side": signal.get("side"),
        "strategy": signal.get("strategy"),
        "context_edge": context_edge,
        "targeting": target,
        "precheck": precheck,
        "sizing": sizing,
        "final_decision": "EMIT_TO_MT5_PAPER" if final_emit else "BLOCK_SIGNAL",
        "paper_lot": paper_lot if final_emit else 0.0,
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


from __future__ import annotations
from math import isfinite

from app.runtime.p2351_regime_detection_engine import approve_strategy_for_regime
from app.runtime.p2352_early_move_trade_management import detect_early_move
from app.runtime.p2343_post_loss_governance_gate import post_loss_gate

def institutional_signal_score(signal: dict, context: dict) -> dict:
    symbol = signal.get("symbol", "")
    side = signal.get("side", "")
    strategy = signal.get("strategy", "SCALP")
    expected_payoff = signal.get("expected_payoff")
    if type(expected_payoff) not in (int, float) or not isfinite(expected_payoff):
        expected_payoff = 0

    score = 0
    reasons = []

    regime = approve_strategy_for_regime(strategy, context)
    if regime["approved"]:
        score += 25
        reasons.append("REGIME_OK")
    else:
        reasons.append("REGIME_BLOCK")

    early = detect_early_move(context)
    if early["decision"] == "EARLY_ENTRY_APPROVED":
        score += 25
        reasons.append("EARLY_MOVE_OK")
    elif early["decision"] == "WAIT_PULLBACK_OR_CONFIRMATION":
        score += 10
        reasons.append("WAIT_CONFIRMATION")
    else:
        reasons.append("EARLY_MOVE_BLOCK")

    post_loss = post_loss_gate(symbol, side, context.get("last_loss") is not False, context)
    if post_loss["status"] == "APPROVED":
        score += 20
        reasons.append("POST_LOSS_GATE_OK")
    else:
        reasons.append("POST_LOSS_GATE_BLOCK")

    correlation_ok = context.get("correlation_ok") is True
    if correlation_ok:
        score += 10
        reasons.append("CORRELATION_OK")
    else:
        reasons.append("CORRELATION_RISK")

    governance_ok = context.get("governance_ok") is True
    if governance_ok:
        score += 10
        reasons.append("GOVERNANCE_OK")
    else:
        reasons.append("GOVERNANCE_BLOCK")

    if expected_payoff >= 3.0:
        score += 10
        reasons.append("PAYOFF_3X_OK")
    else:
        reasons.append("PAYOFF_BELOW_3X")

    score = max(0, min(100, score))

    if (regime.get("approved") is not True or early.get("decision") != "EARLY_ENTRY_APPROVED"
            or post_loss.get("status") != "APPROVED" or not correlation_ok or not governance_ok
            or expected_payoff < 3 or type(context.get("last_loss")) is not bool
            or side not in ("BUY", "SELL") or not isinstance(symbol, str) or not symbol.strip()):
        decision = "BLOCK"
        lot_multiplier = 0.0
        reasons.append("MANDATORY_GATE_FAILED")
    elif score < 40:
        decision = "BLOCK"
        lot_multiplier = 0.0
    elif score < 60:
        decision = "OBSERVE"
        lot_multiplier = 0.0
    elif score < 75:
        decision = "APPROVE_SMALL"
        lot_multiplier = 0.5
    elif score < 90:
        decision = "APPROVE"
        lot_multiplier = 1.0
    else:
        decision = "PRIORITY"
        lot_multiplier = 1.5

    return {
        "symbol": symbol,
        "side": side,
        "strategy": strategy,
        "institutional_score": score,
        "decision": decision,
        "lot_multiplier": lot_multiplier,
        "reasons": reasons,
        "target_payoff_min": 3.0,
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

def health() -> dict:
    return {
        "status": "OK",
        "engine": "P2353_SIGNAL_PRECHECK_FULL_INSTITUTIONAL_SCORE",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

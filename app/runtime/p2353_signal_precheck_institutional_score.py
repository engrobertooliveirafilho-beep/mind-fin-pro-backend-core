from __future__ import annotations

import math

from app.runtime.p2351_regime_detection_engine import approve_strategy_for_regime
from app.runtime.p2352_early_move_trade_management import detect_early_move
from app.runtime.p2343_post_loss_governance_gate import post_loss_gate

def institutional_signal_score(signal: dict, context: dict) -> dict:
    symbol = signal.get("symbol", "")
    side = signal.get("side", "")
    strategy = signal.get("strategy", "SCALP")
    raw_payoff = signal.get("expected_payoff")
    try:
        expected_payoff = float(raw_payoff) if not isinstance(raw_payoff, bool) else math.nan
    except (TypeError, ValueError, OverflowError):
        expected_payoff = math.nan
    if not math.isfinite(expected_payoff) or expected_payoff <= 0:
        return {
            "symbol": symbol, "side": side, "strategy": strategy,
            "institutional_score": 0, "decision": "BLOCK",
            "lot_multiplier": 0.0,
            "reasons": ["PAYOFF_INVALID", "PAYOFF_BELOW_3X"],
            "target_payoff_min": 3.0, "mode": "PAPER_ONLY",
            "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN",
        }

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

    post_loss = post_loss_gate(symbol, side, bool(context.get("last_loss", False)), context)
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

    experimental = (context.get("experimental") is True
                    and context.get("mode") == "PAPER_ONLY"
                    and context.get("real_orders") == "FORBIDDEN"
                    and context.get("ftmo_real") == "FORBIDDEN")
    payoff_min = 2.0 if experimental else 3.0
    if math.isfinite(expected_payoff) and expected_payoff >= 3.0:
        score += 10
        reasons.append("PAYOFF_3X_OK")
    elif experimental and math.isfinite(expected_payoff) and expected_payoff >= payoff_min:
        reasons.append("PAYOFF_EXPERIMENTAL_2X")
    else:
        reasons.append("PAYOFF_BELOW_3X")

    score = max(0, min(100, score))

    mandatory_vetoes = {"REGIME_BLOCK", "EARLY_MOVE_BLOCK", "WAIT_CONFIRMATION",
                        "POST_LOSS_GATE_BLOCK", "CORRELATION_RISK",
                        "GOVERNANCE_BLOCK", "PAYOFF_BELOW_3X"}
    if mandatory_vetoes.intersection(reasons):
        decision = "BLOCK"
        lot_multiplier = 0.0
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
        "target_payoff_min": payoff_min,
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

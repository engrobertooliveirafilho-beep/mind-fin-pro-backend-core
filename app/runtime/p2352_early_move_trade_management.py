from __future__ import annotations

def detect_early_move(context: dict) -> dict:
    adx = float(context.get("adx", 0))
    atr_expansion = bool(context.get("atr_expansion", False))
    breakout = bool(context.get("breakout", False))
    volume_impulse = bool(context.get("volume_impulse", False))
    m1_confirm = bool(context.get("m1_confirm", False))
    m5_confirm = bool(context.get("m5_confirm", False))
    h1_bias = bool(context.get("h1_bias", False))
    spread_ok = bool(context.get("spread_ok", True))

    score = 0
    score += 20 if breakout else 0
    score += 20 if atr_expansion else 0
    score += 15 if volume_impulse else 0
    score += 15 if m1_confirm else 0
    score += 15 if m5_confirm else 0
    score += 10 if h1_bias else 0
    score += 5 if adx >= 20 else 0
    score -= 30 if not spread_ok else 0

    decision = "BLOCK"
    if score >= 80:
        decision = "EARLY_ENTRY_APPROVED"
    elif score >= 60:
        decision = "WAIT_PULLBACK_OR_CONFIRMATION"

    return {
        "early_move_score": max(0, min(100, score)),
        "decision": decision,
        "target_payoff_min": 3.0,
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

def manage_trade(position: dict) -> dict:
    r_multiple = float(position.get("r_multiple", 0))
    open_parts = float(position.get("open_parts", 1.0))
    trend_continues = bool(position.get("trend_continues", False))
    pullback_valid = bool(position.get("pullback_valid", False))

    actions = []

    if r_multiple >= 1.0 and open_parts >= 1.0:
        actions.append("TAKE_PARTIAL_50")
        actions.append("MOVE_STOP_TO_BREAKEVEN")

    if r_multiple >= 2.0:
        actions.append("TRAIL_STOP_BEHIND_STRUCTURE")

    if r_multiple >= 3.0:
        actions.append("LOCK_PROFIT_AND_LET_RUNNER")

    if trend_continues and pullback_valid:
        actions.append("REBUILD_POSITION_SMALL_SIZE")

    if not actions:
        actions.append("HOLD_OR_WAIT")

    return {
        "actions": actions,
        "risk_policy": "NEVER_ADD_TO_LOSER_ONLY_REBUILD_AFTER_PROFIT_OR_VALID_PULLBACK",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

def health() -> dict:
    return {
        "status": "OK",
        "engine": "P2352_EARLY_MOVE_TRIGGER_AND_TRADE_MANAGEMENT_ENGINE",
        "target": "early_trigger|partial_profit|breakeven|trailing|rebuild",
        "mode": "PAPER_ONLY",
    }

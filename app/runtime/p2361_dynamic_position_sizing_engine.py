from __future__ import annotations

def dynamic_paper_lot(ctx: dict) -> dict:
    base_lot = float(ctx.get("base_lot", 0.01))
    score = float(ctx.get("institutional_score", 0))
    payoff = float(ctx.get("expected_payoff", 0))
    drawdown = float(ctx.get("current_drawdown", 0))
    correlation_ok = bool(ctx.get("correlation_ok", True))
    last_trade_loss = bool(ctx.get("last_trade_loss", False))
    rebuild_after_profit = bool(ctx.get("rebuild_after_profit", False))

    multiplier = 0.0
    reason = "BLOCKED"

    if score >= 90 and payoff >= 3 and drawdown <= 5 and correlation_ok and not last_trade_loss:
        multiplier = 1.5
        reason = "PRIORITY_SETUP"
    elif score >= 75 and payoff >= 3 and drawdown <= 8 and correlation_ok and not last_trade_loss:
        multiplier = 1.0
        reason = "STANDARD_APPROVED"
    elif score >= 60 and payoff >= 3 and drawdown <= 10 and correlation_ok:
        multiplier = 0.5
        reason = "SMALL_APPROVED"
    else:
        multiplier = 0.0
        reason = "BLOCKED_BY_SCORE_RISK_OR_PAYOFF"

    if last_trade_loss:
        multiplier = min(multiplier, 0.5)
        reason = "POST_LOSS_REDUCED_OR_BLOCKED"

    if rebuild_after_profit and score >= 75 and payoff >= 3 and correlation_ok:
        multiplier = min(0.5, multiplier)
        reason = "REBUILD_SMALL_SIZE_AFTER_PROFIT"

    lot = round(base_lot * multiplier, 4)

    return {
        "base_lot": base_lot,
        "lot_multiplier": multiplier,
        "recommended_paper_lot": lot,
        "reason": reason,
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "rule": "NEVER_ADD_TO_LOSER_ONLY_SCALE_BY_SCORE_AND_REBUILD_AFTER_PROFIT",
    }

def health() -> dict:
    return {
        "status": "OK",
        "engine": "P2361_DYNAMIC_POSITION_SIZING_ENGINE",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

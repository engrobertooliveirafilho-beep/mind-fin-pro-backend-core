from __future__ import annotations

from app.runtime.p2342_multi_timeframe_revalidation import evaluate

def post_loss_gate(symbol: str, side: str, last_loss: bool, context: dict | None = None) -> dict:
    if (type(last_loss) is not bool or not isinstance(symbol, str) or not symbol.strip()
            or side not in ('BUY', 'SELL') or (context is not None and not isinstance(context, dict))):
        return {'status': 'BLOCKED', 'reason': 'INVALID_GOVERNANCE_INPUT', 'mode': 'PAPER_ONLY', 'real_orders': 'FORBIDDEN', 'ftmo_real': 'FORBIDDEN'}
    context = context or {}

    if not last_loss:
        return {
            "status": "APPROVED",
            "reason": "NO_RECENT_LOSS",
            "symbol": symbol,
            "side": side,
            "mode": "PAPER_ONLY",
            "real_orders": "FORBIDDEN",
        }

    r = evaluate(symbol, side, context)
    approved = r.approved()

    return {
        "status": "APPROVED" if approved else "BLOCKED",
        "reason": "POST_LOSS_REVALIDATION_PASSED" if approved else "POST_LOSS_REVALIDATION_FAILED",
        "symbol": symbol,
        "side": side,
        "required": "M1|M5|M15|H1|trend|volatility|session|support_resistance",
        "score_passed": approved,
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
    }

def health() -> dict:
    return {
        "status": "OK",
        "engine": "P2343_POST_LOSS_GOVERNANCE_GATE",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
    }

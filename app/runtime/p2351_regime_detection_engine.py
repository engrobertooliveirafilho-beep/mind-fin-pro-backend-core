from __future__ import annotations

def detect_regime(context: dict) -> dict:
    atr = float(context.get("atr", 0))
    adx = float(context.get("adx", 0))
    rsi = float(context.get("rsi", 50))
    spread = float(context.get("spread", 0))
    session = str(context.get("session", "UNKNOWN")).upper()
    timeframe = str(context.get("timeframe", "M1")).upper()

    if adx >= 25 and atr > 0:
        regime = "TRENDING"
    elif adx < 18:
        regime = "RANGING"
    else:
        regime = "MIXED"

    volatility = "HIGH_VOLATILITY" if atr >= 1.5 else "NORMAL_VOLATILITY"
    spread_status = "SPREAD_OK" if spread <= 2.0 else "SPREAD_HIGH"

    approved_styles = []
    if timeframe in {"M1", "M5"} and spread_status == "SPREAD_OK":
        approved_styles.append("SCALP")
    if timeframe in {"M5", "M15", "M30", "H1"}:
        approved_styles.append("DAY_TRADE")
    if timeframe in {"H1", "H4", "D1"}:
        approved_styles.append("SWING_TRADE")

    return {
        "regime": regime,
        "volatility": volatility,
        "spread_status": spread_status,
        "session": session,
        "timeframe": timeframe,
        "approved_styles": approved_styles,
        "target_payoff_min": 3.0,
        "target_winrate": "MAXIMIZE_WITHOUT_FALSE_PROMISE",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

def approve_strategy_for_regime(strategy: str, context: dict) -> dict:
    r = detect_regime(context)
    strategy = strategy.upper()

    allowed = False
    reason = "REGIME_NOT_MATCHED"

    if "TREND" in strategy and r["regime"] == "TRENDING":
        allowed = True
        reason = "TREND_STRATEGY_MATCHED_TRENDING_REGIME"
    elif "MEAN_REVERSION" in strategy and r["regime"] == "RANGING":
        allowed = True
        reason = "MEAN_REVERSION_MATCHED_RANGING_REGIME"
    elif strategy in {"SCALP", "DAY_TRADE", "SWING_TRADE"} and strategy in r["approved_styles"]:
        allowed = True
        reason = "STYLE_MATCHED_TIMEFRAME_AND_SPREAD"

    return {
        **r,
        "strategy": strategy,
        "approved": allowed,
        "reason": reason,
        "decision": "APPROVE" if allowed else "BLOCK",
    }

def health() -> dict:
    return {"status": "OK", "engine": "P2351_REGIME_DETECTION_ENGINE", "mode": "PAPER_ONLY"}

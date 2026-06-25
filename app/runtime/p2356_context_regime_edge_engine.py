from __future__ import annotations

def context_signature(ctx: dict) -> str:
    regime = str(ctx.get("regime", "UNKNOWN")).upper()
    cycle = str(ctx.get("cycle", "UNKNOWN")).upper()
    volatility = str(ctx.get("volatility", "NORMAL")).upper()
    session = str(ctx.get("session", "UNKNOWN")).upper()
    structure = str(ctx.get("structure", "UNKNOWN")).upper()

    return f"{regime}|{cycle}|{volatility}|{session}|{structure}"

def classify_context_edge(ctx: dict) -> dict:
    regime = str(ctx.get("regime", "")).upper()
    cycle = str(ctx.get("cycle", "")).upper()
    volatility = str(ctx.get("volatility", "")).upper()
    structure = str(ctx.get("structure", "")).upper()
    session = str(ctx.get("session", "")).upper()

    edge_type = "UNKNOWN_CONTEXT_EDGE"

    if regime == "TRENDING" and structure in {"BREAKOUT", "IMPULSE"}:
        edge_type = "TRENDING_BREAKOUT"
    elif regime == "RANGING" and structure in {"REJECTION", "MEAN_REVERSION"}:
        edge_type = "RANGING_MEAN_REVERSION"
    elif volatility == "HIGH_VOLATILITY" and structure in {"EXPANSION", "BREAKOUT"}:
        edge_type = "HIGH_VOLATILITY_EXPANSION"
    elif volatility == "LOW_VOLATILITY" and structure in {"FAKEOUT", "TRAP"}:
        edge_type = "LOW_VOLATILITY_FAKEOUT"
    elif session in {"LONDON_OPEN", "NY_OPEN"} and structure in {"IMPULSE", "BREAKOUT"}:
        edge_type = "SESSION_OPEN_IMPULSE"
    elif cycle in {"PULLBACK", "RETEST"} and regime == "TRENDING":
        edge_type = "PULLBACK_CONTINUATION"
    elif cycle in {"EXHAUSTION", "CLIMAX"}:
        edge_type = "REVERSAL_EXHAUSTION"

    return {
        "context_signature": context_signature(ctx),
        "edge_type": edge_type,
        "symbol_is_validation_field": True,
        "edge_identity": edge_type,
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

def score_context_edge(stats: dict) -> dict:
    trades = int(stats.get("trades", 0))
    win_rate = float(stats.get("win_rate", 0))
    payoff = float(stats.get("payoff", 0))
    profit_factor = float(stats.get("profit_factor", 0))
    expectancy = float(stats.get("expectancy", 0))
    max_drawdown = float(stats.get("max_drawdown", 100))

    score = 0
    score += min(25, win_rate * 0.25)
    score += min(25, payoff * 8)
    score += min(25, profit_factor * 10)
    score += min(15, max(0, expectancy * 10))
    score += max(0, 10 - max_drawdown)

    passed = (
        trades >= 30 and
        payoff >= 3.0 and
        profit_factor >= 1.5 and
        expectancy > 0 and
        max_drawdown <= 10
    )

    return {
        "context_edge_score": round(min(100, score), 2),
        "passed": passed,
        "decision": "PROMOTE_CONTEXT_EDGE" if passed else "OBSERVE_OR_REJECT_CONTEXT_EDGE",
        "minimum_payoff": 3.0,
        "minimum_trades": 30,
        "mode": "PAPER_ONLY",
    }

def health() -> dict:
    return {"status": "OK", "engine": "P2356_CONTEXT_REGIME_EDGE_ENGINE", "mode": "PAPER_ONLY"}

from __future__ import annotations
from dataclasses import dataclass
from statistics import mean

@dataclass
class BacktestCandidate:
    symbol: str
    style: str
    timeframe: str
    strategy: str
    trades: int
    win_rate: float
    payoff: float
    profit_factor: float
    max_drawdown: float
    expectancy: float

def score_candidate(c: BacktestCandidate) -> dict:
    score = 0
    score += min(30, c.win_rate * 0.3)
    score += min(25, c.payoff * 8)
    score += min(25, c.profit_factor * 10)
    score += max(0, 10 - c.max_drawdown)
    score += min(10, max(0, c.expectancy * 10))

    passed = (
        c.trades >= 30 and
        c.payoff >= 3.0 and
        c.profit_factor >= 1.5 and
        c.max_drawdown <= 10 and
        c.expectancy > 0
    )

    return {
        "symbol": c.symbol,
        "style": c.style,
        "timeframe": c.timeframe,
        "strategy": c.strategy,
        "base_lot": 0.01,
        "trades": c.trades,
        "win_rate": c.win_rate,
        "payoff": c.payoff,
        "profit_factor": c.profit_factor,
        "max_drawdown": c.max_drawdown,
        "expectancy": c.expectancy,
        "score": round(min(100, score), 2),
        "passed": passed,
        "decision": "PROMOTE_TO_FORWARD_PAPER" if passed else "REJECT_OR_OBSERVE",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
    }

def optimize(candidates: list[dict]) -> dict:
    scored = [score_candidate(BacktestCandidate(**c)) for c in candidates]
    promoted = [x for x in scored if x["passed"]]
    return {
        "program": "P2355_MULTI_YEAR_MULTI_ASSET_BACKTEST_OPTIMIZER",
        "base_lot": 0.01,
        "target_payoff_min": 3.0,
        "symbols": sorted(set(x["symbol"] for x in scored)),
        "candidates_total": len(scored),
        "promoted": len(promoted),
        "ranking": sorted(scored, key=lambda x: x["score"], reverse=True),
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

def health() -> dict:
    return {"status": "OK", "engine": "P2355_MULTI_YEAR_MULTI_ASSET_BACKTEST_OPTIMIZER", "mode": "PAPER_ONLY"}

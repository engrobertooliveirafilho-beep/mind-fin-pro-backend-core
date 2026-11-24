from __future__ import annotations
from math import isfinite

def validate_walk_forward(samples: list[dict]) -> dict:
    passed = []
    rejected = []

    for s in samples:
        keys = ("train_profit_factor", "test_profit_factor", "train_payoff", "test_payoff", "test_max_drawdown")
        if (any(type(s.get(k)) not in (int, float) or not isfinite(s[k]) for k in keys)
                or type(s.get("test_trades")) is not int
                or s["test_trades"] < 0 or s["train_profit_factor"] <= 0
                or s["test_profit_factor"] < 0 or not 0 <= s["test_max_drawdown"] <= 100):
            rejected.append({**s, "walk_forward_passed": False, "decision": "REJECT_INVALID_METRICS", "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN"})
            continue
        train_pf = float(s.get("train_profit_factor", 0))
        test_pf = float(s.get("test_profit_factor", 0))
        train_payoff = float(s.get("train_payoff", 0))
        test_payoff = float(s.get("test_payoff", 0))
        test_trades = int(s.get("test_trades", 0))
        dd = float(s.get("test_max_drawdown", 100))

        degradation = 0 if train_pf == 0 else max(0, (train_pf - test_pf) / train_pf)

        ok = (
            test_trades >= 30 and
            test_pf >= 1.5 and
            test_payoff >= 3.0 and
            dd <= 10 and
            degradation <= 0.35
        )

        row = {
            **s,
            "degradation": round(degradation, 4),
            "walk_forward_passed": ok,
            "decision": "PROMOTE_CONTEXT_EDGE" if ok else "REJECT_OVERFIT_OR_WEAK_CONTEXT",
            "mode": "PAPER_ONLY",
            "real_orders": "FORBIDDEN",
        }

        (passed if ok else rejected).append(row)

    return {
        "program": "P2357_CONTEXT_EDGE_WALK_FORWARD_VALIDATOR",
        "samples_total": len(samples),
        "passed": len(passed),
        "rejected": len(rejected),
        "passed_rows": passed,
        "rejected_rows": rejected,
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

def health() -> dict:
    return {"status": "OK", "engine": "P2357_CONTEXT_EDGE_WALK_FORWARD_VALIDATOR", "mode": "PAPER_ONLY"}

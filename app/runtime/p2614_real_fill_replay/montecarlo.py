import math
import random

def monte_carlo_from_trades(trades, initial_capital=100.0, risk_pct=0.01, runs=500):
    if isinstance(initial_capital, bool) or not isinstance(initial_capital, (int, float)) or not math.isfinite(initial_capital) or initial_capital <= 0:
        raise ValueError("INVALID_INITIAL_CAPITAL")
    if isinstance(risk_pct, bool) or not isinstance(risk_pct, (int, float)) or not math.isfinite(risk_pct) or not 0 <= risk_pct <= 1:
        raise ValueError("INVALID_RISK_PCT")
    if isinstance(runs, bool) or not isinstance(runs, int) or runs < 1:
        raise ValueError("INVALID_RUN_COUNT")
    if not isinstance(trades, (list, tuple)):
        raise ValueError("INVALID_TRADES_COLLECTION")

    rs = []
    for index, trade in enumerate(trades):
        if not isinstance(trade, dict) or "r" not in trade:
            raise ValueError(f"INVALID_TRADE_RECORD:{index}")
        value = trade["r"]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"INVALID_TRADE_R:{index}")
        rs.append(float(value))

    if not rs:
        return {"runs": 0, "p50_final": float(initial_capital), "p95_dd": 0.0}

    finals = []
    dds = []
    for seed in range(runs):
        sample = rs[:]
        random.Random(seed).shuffle(sample)
        capital = float(initial_capital)
        peak = capital
        max_dd = 0.0
        for value in sample:
            capital = max(0.01, capital + capital * float(risk_pct) * value)
            if not math.isfinite(capital):
                raise ValueError("NONFINITE_MONTE_CARLO_EQUITY")
            peak = max(peak, capital)
            max_dd = max(max_dd, (peak - capital) / peak * 100)
        finals.append(capital)
        dds.append(max_dd)

    finals.sort()
    dds.sort()
    return {
        "runs": runs,
        "p05_final": round(finals[min(int(runs * 0.05), runs - 1)], 6),
        "p50_final": round(finals[min(int(runs * 0.50), runs - 1)], 6),
        "p95_final": round(finals[min(int(runs * 0.95), runs - 1)], 6),
        "p50_dd": round(dds[min(int(runs * 0.50), runs - 1)], 6),
        "p95_dd": round(dds[min(int(runs * 0.95), runs - 1)], 6),
    }

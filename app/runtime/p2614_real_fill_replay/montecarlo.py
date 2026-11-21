import math
import random

def _finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(float(value))
    except (OverflowError, TypeError, ValueError):
        return False

def monte_carlo_from_trades(trades, initial_capital=100.0, risk_pct=0.01, runs=500):
    if not _finite_number(initial_capital) or initial_capital <= 0:
        raise ValueError("INVALID_INITIAL_CAPITAL")
    if not _finite_number(risk_pct) or not 0 <= risk_pct <= 1:
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
        if not _finite_number(value):
            raise ValueError(f"INVALID_TRADE_R:{index}")
        rs.append(float(value))

    if not rs:
        return {"method": "bootstrap_with_replacement", "runs": 0,
                "p05_final": float(initial_capital), "p50_final": float(initial_capital),
                "p95_final": float(initial_capital), "p50_dd": 0.0, "p95_dd": 0.0}

    finals = []
    dds = []
    for seed in range(runs):
        rng = random.Random(seed)
        sample = [rng.choice(rs) for _ in range(len(rs))]
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
    percentile = lambda values, p: values[min(math.ceil((len(values) - 1) * p), len(values) - 1)]
    return {
        "method": "bootstrap_with_replacement",
        "runs": runs,
        "p05_final": round(percentile(finals, 0.05), 6),
        "p50_final": round(percentile(finals, 0.50), 6),
        "p95_final": round(percentile(finals, 0.95), 6),
        "p50_dd": round(percentile(dds, 0.50), 6),
        "p95_dd": round(percentile(dds, 0.95), 6),
    }

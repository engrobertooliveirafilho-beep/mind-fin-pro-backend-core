"""P2614 Monte Carlo hardening: offline, deterministic, PAPER-only."""
import math
import random

def monte_carlo_from_trades(trades, initial_capital=100.0, risk_pct=0.01, runs=500):
    if isinstance(runs, bool) or not isinstance(runs, int) or runs < 1:
        raise ValueError("runs must be a positive integer")
    if not math.isfinite(initial_capital) or initial_capital <= 0:
        raise ValueError("initial_capital must be positive and finite")
    if not math.isfinite(risk_pct) or not 0 < risk_pct <= 1:
        raise ValueError("risk_pct must be in (0, 1]")
    rs = []
    for trade in trades:
        r = float(trade["r"])
        if not math.isfinite(r):
            raise ValueError("nonfinite trade R")
        rs.append(r)
    if not rs:
        return {"runs": 0, "p50_final": initial_capital, "p95_dd": 0}
    finals, dds = [], []
    for k in range(runs):
        sample = rs[:]
        random.Random(k).shuffle(sample)
        cap = peak = float(initial_capital)
        max_dd = 0.0
        for r in sample:
            cap = max(0.01, cap * (1 + risk_pct * r))
            peak = max(peak, cap)
            max_dd = max(max_dd, (peak-cap)/peak*100)
        finals.append(cap)
        dds.append(max_dd)
    finals.sort()
    dds.sort()
    ix = lambda p: min(runs-1, int(runs*p))
    return {"runs": runs, "p05_final": round(finals[ix(.05)], 6),
            "p50_final": round(finals[ix(.50)], 6),
            "p95_final": round(finals[ix(.95)], 6),
            "p50_dd": round(dds[ix(.50)], 6),
            "p95_dd": round(dds[ix(.95)], 6)}

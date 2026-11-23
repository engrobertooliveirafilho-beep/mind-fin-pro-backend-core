import math
import random


def monte_carlo_from_trades(trades, initial_capital=100.0, risk_pct=0.01, runs=500):
    if not isinstance(trades, (list, tuple)) or isinstance(runs, bool) or not isinstance(runs, int) or runs < 1:
        raise ValueError('INVALID_MONTE_CARLO_INPUT')
    for value, positive in ((initial_capital, True), (risk_pct, True)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or (positive and value <= 0):
            raise ValueError('INVALID_MONTE_CARLO_INPUT')
    if risk_pct > 1:
        raise ValueError('INVALID_MONTE_CARLO_INPUT')
    rs=[]
    for t in trades:
        if not isinstance(t, dict) or isinstance(t.get('r'), bool) or not isinstance(t.get('r'), (int, float)) or not math.isfinite(t['r']):
            raise ValueError('INVALID_MONTE_CARLO_TRADE')
        rs.append(float(t['r']))
    if not rs:
        return {'runs': 0, 'p50_final': initial_capital, 'p95_dd': 0}
    finals=[]
    dds=[]
    for k in range(runs):
        rng=random.Random(k)
        sample=[rs[rng.randrange(len(rs))] for _ in rs]
        cap=initial_capital
        peak=cap
        max_dd=0.0
        for r in sample:
            cap=max(0.01,cap+cap*risk_pct*r)
            peak=max(peak,cap)
            max_dd=max(max_dd,(peak-cap)/peak*100)
        finals.append(cap)
        dds.append(max_dd)
    finals.sort()
    dds.sort()
    def pct(values, p):
        return round(values[min(len(values)-1, int((len(values)-1)*p))],6)
    return {'runs': runs, 'p05_final': pct(finals,.05), 'p50_final': pct(finals,.50), 'p95_final': pct(finals,.95), 'p50_dd': pct(dds,.50), 'p95_dd': pct(dds,.95)}

import random, statistics

def monte_carlo_from_trades(trades, initial_capital=100.0, risk_pct=0.01, runs=500):
    rs=[float(t["r"]) for t in trades]
    if not rs:
        return {"runs":0,"p50_final":initial_capital,"p95_dd":0}
    finals=[]
    dds=[]
    for k in range(runs):
        sample=rs[:]
        random.Random(k).shuffle(sample)
        cap=initial_capital
        peak=cap
        max_dd=0
        for r in sample:
            cap=max(0.01,cap+cap*risk_pct*r)
            peak=max(peak,cap)
            max_dd=max(max_dd,(peak-cap)/peak*100)
        finals.append(cap)
        dds.append(max_dd)
    finals=sorted(finals)
    dds=sorted(dds)
    return {
        "runs":runs,
        "p05_final":round(finals[int(runs*0.05)],6),
        "p50_final":round(finals[int(runs*0.50)],6),
        "p95_final":round(finals[int(runs*0.95)],6),
        "p50_dd":round(dds[int(runs*0.50)],6),
        "p95_dd":round(dds[int(runs*0.95)],6)
    }

import math

def portfolio_metrics(series):
    if not series or any(not isinstance(s,dict) or not s for s in series):
        raise ValueError('Missing aligned net returns')
    dates=sorted(series[0])
    if any(set(s)!=set(dates) for s in series):
        raise ValueError('Unaligned returns')
    if any(not math.isfinite(v) for s in series for v in s.values()):
        raise ValueError('Nonfinite returns')
    returns=[sum(s[t] for s in series)/len(series) for t in dates]
    gain=sum(max(r,0) for r in returns); loss=sum(max(-r,0) for r in returns)
    equity=peak=dd=0
    for r in returns:
        equity+=r; peak=max(peak,equity); dd=max(dd,peak-equity)
    return dict(pf=gain/loss if loss else None,max_dd_r=dd,net_r=equity,hard_pass=False,decision='RESEARCH_ONLY_PROVENANCE_PENDING',runtime_promotion_allowed=False,real_execution_allowed=False)

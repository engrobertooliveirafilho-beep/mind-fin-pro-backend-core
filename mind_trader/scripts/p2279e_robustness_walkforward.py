from pathlib import Path
import csv, json, math
from statistics import mean, pstdev

from datetime import datetime

def read_rows(path):
    rows=[]
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t=datetime.fromisoformat((r.get("time") or r.get("date") or r.get("timestamp")).replace(".", "-", 2))
            v={k:float(r[k]) for k in ("open","high","low","close")}
            if not all(math.isfinite(x) and x>0 for x in v.values()) or v["low"]>min(v["open"],v["close"]) or v["high"]<max(v["open"],v["close"]) or (rows and t<=rows[-1]["time"]):
                raise ValueError("invalid OHLC or chronology")
            rows.append(dict(time=t,**v))
    return rows

def sma(vals,p):
    out=[None]*len(vals); s=0
    for i,v in enumerate(vals):
        s+=v
        if i>=p: s-=vals[i-p]
        if i>=p-1: out[i]=s/p
    return out

def ema(vals,p):
    out=[None]*len(vals)
    if not vals: return out
    k=2/(p+1); e=vals[0]
    for i,v in enumerate(vals):
        e = v if i==0 else v*k + e*(1-k)
        if i>=p-1: out[i]=e
    return out

def bt(rows,strategy,params,*,round_trip_cost):
    if not math.isfinite(round_trip_cost) or round_trip_cost<=0: raise ValueError("positive explicit cost required")
    fast,slow=[int(x) for x in params.split(",")]
    if not 0<fast<slow or not strategy.startswith(("EMA","SMA")): raise ValueError("invalid strategy")
    closes=[x["close"] for x in rows]
    if len(closes)<slow+30: return None
    f=ema(closes,fast) if strategy.startswith("EMA") else sma(closes,fast)
    s=ema(closes,slow) if strategy.startswith("EMA") else sma(closes,slow)

    pos=None; entry=0; trades=[]; eq=[0]; total=0
    for i in range(1,len(rows)-1):
        if f[i-1] is None or s[i-1] is None or f[i] is None or s[i] is None: continue
        sig=None
        if f[i-1] <= s[i-1] and f[i] > s[i]: sig="BUY"
        elif f[i-1] >= s[i-1] and f[i] < s[i]: sig="SELL"
        if not sig: continue
        price=rows[i+1]["open"]
        if pos:
            pnl=(price-entry) if pos=="BUY" else (entry-price)
            pnl-=round_trip_cost; trades.append(pnl); total+=pnl; eq.append(total)
        pos=sig; entry=price
    if pos:
        price=rows[-1]["close"]
        pnl=(price-entry) if pos=="BUY" else (entry-price)
        pnl-=round_trip_cost; trades.append(pnl); total+=pnl; eq.append(total)
    if len(trades)<5: return None
    wins=[x for x in trades if x>0]; losses=[x for x in trades if x<0]
    gw=sum(wins); gl=abs(sum(losses))
    pf=gw/gl if gl else None
    wr=len(wins)/len(trades)*100
    peak=0; dd=0
    for x in eq:
        peak=max(peak,x); dd=max(dd,peak-x)
    return {"expectancy":total/len(trades),"profit_factor":pf,"trades":len(trades),"pf":pf,"winrate":wr,"netprofit":total,"maxdd":dd}


def evaluate_holdout(rows,strategy,params,*,round_trip_cost,authority):
    # First half reserved for development; caller must freeze parameters before holdout.
    n=len(rows)
    if n<500: raise ValueError("insufficient rows")
    start=n//2
    windows=[bt(rows[start+(n-start)*i//4:start+(n-start)*(i+1)//4],strategy,params,round_trip_cost=round_trip_cost) for i in range(4)]
    if any(w is None or w["profit_factor"] is None for w in windows):
        return {"passed":False,"production":"BLOCKED","live":"FORBIDDEN","windows":windows}
    decision=authority(windows)
    return {"passed":decision.get("passed") is True and all(w["expectancy"]>0 and w["profit_factor"]>=1.05 for w in windows),"production":"BLOCKED","live":"FORBIDDEN","windows":windows}


def evaluate_canonical_holdout(rows, strategy, params, *, round_trip_cost):
    from mind_trader.app.validation.walk_forward_authority import walk_forward_authority
    return evaluate_holdout(rows, strategy, params, round_trip_cost=round_trip_cost, authority=walk_forward_authority)


def freeze_development(rows, strategy, params, *, round_trip_cost):
    """Commit parameters and development prefix; persist externally before holdout access."""
    import hashlib
    if len(rows)<250: raise ValueError('insufficient development rows')
    payload=dict(strategy=strategy,params=params,cost=round_trip_cost,development_count=len(rows),development_hash=hashlib.sha256(json.dumps(rows,default=str,sort_keys=True).encode()).hexdigest())
    return json.dumps(payload,sort_keys=True)


def evaluate_frozen_holdout(rows, commitment, *, expected_sha256):
    import hashlib
    if hashlib.sha256(commitment.encode()).hexdigest()!=expected_sha256: raise ValueError('commitment mismatch')
    p=json.loads(commitment)
    if p['development_count']!=len(rows)//2: raise ValueError('split mismatch')
    if freeze_development(rows[:len(rows)//2],p['strategy'],p['params'],round_trip_cost=p['cost'])!=commitment: raise ValueError('development changed')
    return evaluate_canonical_holdout(rows,p['strategy'],p['params'],round_trip_cost=p['cost'])

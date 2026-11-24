from pathlib import Path
import csv, math, json
from statistics import mean

symbols = ["EURUSD","GBPUSD","USDJPY","USDCHF","AUDUSD","NZDUSD","USDCAD","XAUUSD","US100","US500","GER40","UK100","JP225"]
tfs = ["M15","M30","H1","H4","D1"]

strategies = [
    ("EMA_CROSS","9,34"),
    ("EMA_CROSS","13,55"),
    ("EMA_CROSS","21,55"),
    ("SMA_CROSS","9,34"),
    ("SMA_CROSS","13,55"),
    ("SMA_CROSS","20,50"),
    ("SMA_CROSS","50,200"),
]

def read_rows(path):
    from datetime import datetime
    rows=[]
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t=datetime.fromisoformat((r.get("time") or r.get("date") or r.get("timestamp")).replace(".", "-", 2))
            v={k:float(r[k]) for k in ("open","high","low","close")}
            if not all(math.isfinite(x) and x>0 for x in v.values()) or v['low']>min(v['open'],v['close']) or v['high']<max(v['open'],v['close']) or (rows and t<=rows[-1]['time']):
                raise ValueError('invalid OHLC or chronology')
            rows.append(dict(time=t,**v))
    return rows

def sma(vals, p):
    out=[None]*len(vals)
    s=0.0
    for i,v in enumerate(vals):
        s+=v
        if i>=p:
            s-=vals[i-p]
        if i>=p-1:
            out[i]=s/p
    return out

def ema(vals, p):
    out=[None]*len(vals)
    if not vals:
        return out
    k=2/(p+1)
    e=vals[0]
    for i,v in enumerate(vals):
        if i==0:
            e=v
        else:
            e=v*k + e*(1-k)
        if i>=p-1:
            out[i]=e
    return out

def max_drawdown(equity):
    peak=0.0
    dd=0.0
    for x in equity:
        if x>peak: peak=x
        d=peak-x
        if d>dd: dd=d
    return dd

def backtest(rows, strategy, params, *, round_trip_cost):
    if not math.isfinite(round_trip_cost) or round_trip_cost<=0: raise ValueError("positive cost required")
    if strategy not in ("EMA_CROSS","SMA_CROSS"): raise ValueError("invalid strategy")
    fast, slow = [int(x) for x in params.split(",")]
    if not 0<fast<slow: raise ValueError("invalid periods")
    closes=[r["close"] for r in rows]

    if len(closes) < slow + 20:
        return None

    if strategy.startswith("EMA"):
        f=ema(closes,fast); s=ema(closes,slow)
    else:
        f=sma(closes,fast); s=sma(closes,slow)

    pos=None
    entry=0.0
    trades=[]
    equity=[0.0]
    pnl_total=0.0

    for i in range(1, len(rows)-1):
        if f[i-1] is None or s[i-1] is None or f[i] is None or s[i] is None:
            continue

        signal=None
        if f[i-1] <= s[i-1] and f[i] > s[i]:
            signal="BUY"
        elif f[i-1] >= s[i-1] and f[i] < s[i]:
            signal="SELL"

        price=rows[i+1]["open"]

        if signal:
            if pos is not None:
                pnl = (price-entry) if pos=="BUY" else (entry-price)
                trades.append(pnl-round_trip_cost)
                pnl_total += pnl-round_trip_cost
                equity.append(pnl_total)
            pos=signal
            entry=price

    if pos is not None:
        price=rows[-1]["close"]
        pnl = (price-entry) if pos=="BUY" else (entry-price)
        trades.append(pnl-round_trip_cost)
        pnl_total += pnl-round_trip_cost
        equity.append(pnl_total)

    if len(trades) < 20:
        return None

    wins=[x for x in trades if x>0]
    losses=[x for x in trades if x<0]
    gross_win=sum(wins)
    gross_loss=abs(sum(losses))

    pf = gross_win/gross_loss if gross_loss>0 else None
    if pf is None: return None
    winrate = len(wins)/len(trades)*100
    payoff = (mean(wins)/abs(mean(losses))) if wins and losses else 0.0
    dd = max_drawdown(equity)

    return {
        "trades": len(trades),
        "pf": round(pf,4),
        "winrate": round(winrate,2),
        "payoff": round(payoff,4),
        "maxdd": round(dd,6),
        "netprofit": round(pnl_total,6),
    }

def run(data, costs):
    results=[]; blocked=[]
    for sym in symbols:
        for tf in tfs:
            path=Path(data)/f"MT5_{sym}_{tf}_raw.csv"
            try:
                rows=read_rows(path)
                if len(rows)<500: raise ValueError("insufficient rows")
                cost=costs[sym]
                if not math.isfinite(cost) or cost<=0: raise ValueError("invalid cost")
            except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
                blocked.append((sym,tf,str(exc))); continue
            for strategy,params in strategies:
                r=backtest(rows,strategy,params,round_trip_cost=cost)
                if r is not None:
                    results.append(dict(symbol=sym,timeframe=tf,strategy=strategy,params=params,**r,status="RESEARCH",mode="PAPER_ONLY",real_orders="FORBIDDEN"))
    return dict(results=results,blocked=blocked,production="BLOCKED",live="FORBIDDEN")

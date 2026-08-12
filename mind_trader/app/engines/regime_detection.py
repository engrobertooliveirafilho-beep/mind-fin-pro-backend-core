import json, statistics
from pathlib import Path
from mind_trader.app.backtest.market_core import load_ohlcv

def _lin_slope(vals):
    n=len(vals)
    if n<2: return 0.0
    xs=range(n); mx=sum(xs)/n; my=sum(vals)/n
    den=sum((x-mx)**2 for x in xs)
    return 0.0 if den==0 else sum((x-mx)*(y-my) for x,y in zip(xs,vals))/den

def _atr_proxy(rows):
    trs=[]
    prev=None
    for r in rows:
        h=float(r["high"]); l=float(r["low"]); c=float(r["close"])
        tr=(h-l) if prev is None else max(h-l, abs(h-prev), abs(l-prev))
        trs.append(tr); prev=c
    return statistics.mean(trs) if trs else 0.0

def detect_regime_from_rows(rows, window=30):
    if len(rows)<window:
        return {"regime":"UNDEFINED","reason":"INSUFFICIENT_DATA","trade_allowed":False}
    part=rows[-window:]
    closes=[float(r["close"]) for r in part]
    highs=[float(r["high"]) for r in part]
    lows=[float(r["low"]) for r in part]
    atr=_atr_proxy(part)
    mean_close=statistics.mean(closes)
    slope=_lin_slope(closes)
    total_range=max(highs)-min(lows)
    normalized_slope=0 if mean_close==0 else slope/mean_close
    normalized_atr=0 if mean_close==0 else atr/mean_close
    range_ratio=0 if mean_close==0 else total_range/mean_close

    if normalized_atr < 0.0015 and range_ratio < 0.01:
        regime="COMPRESSION_LOW_VOL"
    elif normalized_atr > 0.006 or range_ratio > 0.04:
        regime="EXPANSION_HIGH_VOL"
    elif normalized_slope > 0.00035:
        regime="TREND_UP"
    elif normalized_slope < -0.00035:
        regime="TREND_DOWN"
    elif range_ratio < 0.025:
        regime="RANGE_SIDEWAYS"
    else:
        regime="MIXED_TRANSITION"

    return {
        "regime":regime,
        "window":window,
        "slope":slope,
        "normalized_slope":normalized_slope,
        "atr_proxy":atr,
        "normalized_atr":normalized_atr,
        "range_ratio":range_ratio,
        "trade_allowed": regime!="UNDEFINED"
    }

def detect_regime(symbol,timeframe,db_path="mind_trader/data/market.sqlite",window=30):
    rows=load_ohlcv(symbol,timeframe,db_path)
    return detect_regime_from_rows(rows,window)

def regime_series(rows, window=30):
    out=[]
    for i in range(window,len(rows)+1):
        r=detect_regime_from_rows(rows[:i],window)
        r["index"]=i-1
        r["ts"]=rows[i-1]["ts"]
        out.append(r)
    return out

def require_defined_regime(regime_report):
    if not regime_report.get("trade_allowed") or regime_report.get("regime")=="UNDEFINED":
        return False, "BLOCKED_REGIME_UNDEFINED"
    return True, "REGIME_OK"

def save_regime_report(report,path="mind_trader/reports/P8.31_regime_report.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return path

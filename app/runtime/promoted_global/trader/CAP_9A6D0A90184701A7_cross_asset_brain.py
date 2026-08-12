import json, statistics
from pathlib import Path
from mind_trader.app.backtest.market_core import load_ohlcv
from mind_trader.app.engines.regime_detection import detect_regime_from_rows

def pct_returns(rows):
    out=[]
    for i in range(1,len(rows)):
        prev=float(rows[i-1]["close"]); cur=float(rows[i]["close"])
        if prev != 0:
            out.append({"ts":rows[i]["ts"],"ret":(cur-prev)/prev})
    return out

def align_returns(rows_a, rows_b):
    a={x["ts"]:x["ret"] for x in pct_returns(rows_a)}
    b={x["ts"]:x["ret"] for x in pct_returns(rows_b)}
    ts=sorted(set(a)&set(b))
    return [a[t] for t in ts],[b[t] for t in ts],ts

def corr(xs,ys):
    if len(xs)<3 or len(xs)!=len(ys): return 0.0
    mx=statistics.mean(xs); my=statistics.mean(ys)
    sx=sum((x-mx)**2 for x in xs); sy=sum((y-my)**2 for y in ys)
    den=(sx*sy)**0.5
    return 0.0 if den==0 else sum((x-mx)*(y-my) for x,y in zip(xs,ys))/den

def rolling_correlation(rows_a, rows_b, window=30):
    xs,ys,ts=align_returns(rows_a,rows_b)
    out=[]
    for i in range(window,len(xs)+1):
        out.append({"ts":ts[i-1],"correlation":corr(xs[i-window:i],ys[i-window:i]),"sample_size":window})
    return out

def lag_correlation(rows_leader, rows_follower, lag=1):
    x,y,ts=align_returns(rows_leader,rows_follower)
    if len(x)<=lag+3: return {"lag":lag,"correlation":0.0,"sample_size":0}
    return {"lag":lag,"correlation":corr(x[:-lag],y[lag:]),"sample_size":len(x)-lag}

def cross_asset_report(symbol_a, symbol_b, timeframe, db_path="mind_trader/data/market.sqlite", window=30):
    a=load_ohlcv(symbol_a,timeframe,db_path)
    b=load_ohlcv(symbol_b,timeframe,db_path)
    if len(a)<window+5 or len(b)<window+5:
        return {"asset_a":symbol_a,"asset_b":symbol_b,"decision":"INSUFFICIENT_DATA","edge_claim":"NONE","production":"BLOCKED"}
    xs,ys,ts=align_returns(a,b)
    base=corr(xs,ys)
    roll=rolling_correlation(a,b,window)
    reg=detect_regime_from_rows(a,window).get("regime","UNDEFINED")
    lag_ab=lag_correlation(a,b,1)
    lag_ba=lag_correlation(b,a,1)
    hypothesis=[]
    if abs(base)>=0.6: hypothesis.append("STRONG_SYNCHRONY_STATISTICAL_RELATION")
    if lag_ab["correlation"]-base>0.1: hypothesis.append(f"{symbol_a}_LEADS_{symbol_b}_POSSIBLE")
    if lag_ba["correlation"]-base>0.1: hypothesis.append(f"{symbol_b}_LEADS_{symbol_a}_POSSIBLE")
    if abs(base)<0.15: hypothesis.append("POSSIBLE_DECOUPLING")
    return {
        "asset_a":symbol_a,
        "asset_b":symbol_b,
        "timeframe":timeframe,
        "correlation":base,
        "regime":reg,
        "sample_size":len(xs),
        "rolling_last":roll[-1] if roll else None,
        "lag_ab":lag_ab,
        "lag_ba":lag_ba,
        "hypothesis":hypothesis,
        "causality_claim":"FORBIDDEN",
        "edge_claim":"NONE",
        "decision":"RESEARCH_HYPOTHESIS_ONLY",
        "production":"BLOCKED"
    }

def matrix_report(symbols, timeframe, db_path="mind_trader/data/market.sqlite", window=30):
    out=[]
    for i,a in enumerate(symbols):
        for b in symbols[i+1:]:
            out.append(cross_asset_report(a,b,timeframe,db_path,window))
    return out

def save_cross_asset_report(report,path="mind_trader/reports/P8.34_cross_asset_report.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return path

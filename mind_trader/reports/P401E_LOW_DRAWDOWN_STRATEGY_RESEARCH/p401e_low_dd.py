import json, csv, statistics, hashlib
from pathlib import Path
from datetime import datetime, UTC

OUT=Path("reports/P401E_LOW_DRAWDOWN_STRATEGY_RESEARCH")
DATA=Path("data/normalized")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

FAMILIES=["SMA_CROSS","EMA_CROSS","RSI_REVERSION","BREAKOUT","MOMENTUM","PULLBACK"]
RISK_MODELS=[
    {"sl":0.003,"tp":0.006,"trail":0.002,"risk":0.0025},
    {"sl":0.005,"tp":0.010,"trail":0.003,"risk":0.0020},
    {"sl":0.007,"tp":0.014,"trail":0.004,"risk":0.0015},
    {"sl":0.010,"tp":0.020,"trail":0.006,"risk":0.0010}
]

def sig(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,default=str).encode()).hexdigest()[:24]

def read_close(path, limit=1000):
    closes=[]
    try:
        with open(path,newline="",encoding="utf-8") as f:
            for r in csv.DictReader(f):
                c=float(r.get("close",0) or 0)
                if c>0: closes.append(c)
    except Exception:
        pass
    return closes[-limit:]

def asset_tf(path):
    b=path.name.replace("_normalized.csv","")
    p=b.split("_")
    return p[0] if p else "UNKNOWN", p[1] if len(p)>1 else "UNKNOWN"

def simulate(closes,family,risk):
    if len(closes)<100:
        return None
    trades=[]
    equity=1.0
    peak=1.0
    maxdd=0
    for i in range(60,len(closes)-1,5):
        ma20=statistics.mean(closes[max(0,i-20):i])
        ma50=statistics.mean(closes[max(0,i-50):i])
        direction=1 if closes[i] > ma20 else -1
        if "REVERSION" in family:
            direction=-direction
        if "CROSS" in family:
            direction=1 if ma20>ma50 else -1
        ret=(closes[i+1]/closes[i]-1)*direction
        ret=max(-risk["sl"],min(risk["tp"],ret))
        equity *= (1 + ret * (risk["risk"]/0.0025))
        peak=max(peak,equity)
        maxdd=max(maxdd,(peak-equity)/peak)
        trades.append(ret)
    wins=sum(x for x in trades if x>0)
    losses=sum(abs(x) for x in trades if x<0) or 1e-9
    pf=wins/losses
    return {
        "trades":len(trades),
        "profit_factor":round(pf,6),
        "max_drawdown":round(maxdd,6),
        "approved_low_dd":pf>=1.25 and maxdd<=0.08 and len(trades)>=30
    }

def run(max_datasets=166):
    OUT.mkdir(parents=True,exist_ok=True)
    files=list(DATA.glob("*_normalized.csv"))[:max_datasets]
    results=[]
    for f in files:
        closes=read_close(f)
        asset,tf=asset_tf(f)
        for fam in FAMILIES:
            for rm in RISK_MODELS:
                r=simulate(closes,fam,rm)
                if not r: continue
                results.append({
                    "job_id":sig([str(f),fam,rm]),
                    "dataset":str(f),
                    "asset":asset,
                    "timeframe":tf,
                    "family":fam,
                    "risk_model":rm,
                    **r,
                    **BLOCKS
                })
    candidates=[x for x in results if x["approved_low_dd"]]
    (OUT/"p401e_low_dd_results.json").write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p401e_low_dd_candidates.json").write_text(json.dumps(candidates,indent=2,ensure_ascii=False),encoding="utf-8")
    report={
        "STATUS":"P401E_LOW_DRAWDOWN_STRATEGY_RESEARCH_COMPLETED",
        "RESULTS":len(results),
        "LOW_DD_CANDIDATES":len(candidates),
        "BEST_DD":min([x["max_drawdown"] for x in results], default=None),
        "BEST_PF":max([x["profit_factor"] for x in results], default=None),
        "NEXT":"P401F_LOW_DD_WALK_FORWARD_MONTE_CARLO" if candidates else "EXPAND_LOW_DD_RESEARCH",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p401e_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))

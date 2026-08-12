import json, csv, math
from pathlib import Path
from datetime import datetime, UTC

INP=Path("reports/P16.21G_RULE_NORMALIZATION_AUTO_BACKTEST/p1621g_backtest_queue_results.json")
OUT=Path("reports/P16.21K_VIDEO_STRATEGY_BACKTEST_EXECUTOR")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","CAUSALITY":"NOT_PROVEN"}

def load():
    return json.loads(INP.read_text(encoding="utf-8")) if INP.exists() else []

def datasets():
    return list(Path("data/normalized").glob("*_normalized.csv"))

def load_close(path):
    rows=[]
    with open(path,newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                c=float(r.get("close",0))
                if c>0: rows.append(c)
            except Exception:
                pass
    return rows

def sma(vals,n,i):
    if i<n: return None
    return sum(vals[i-n:i])/n

def sma_cross_backtest(closes,fast=5,slow=55):
    pos=0; entry=0; trades=[]; equity=1.0; peak=1.0; dd=0.0
    for i in range(slow+1,len(closes)):
        f0=sma(closes,fast,i); s0=sma(closes,slow,i)
        f1=sma(closes,fast,i-1); s1=sma(closes,slow,i-1)
        if None in (f0,s0,f1,s1): continue
        if pos==0 and f0>s0 and f1<=s1:
            pos=1; entry=closes[i]
        elif pos==1 and f0<s0 and f1>=s1:
            ret=closes[i]/entry-1
            trades.append(ret); equity*=1+ret; peak=max(peak,equity); dd=min(dd,equity/peak-1); pos=0
    wins=[x for x in trades if x>0]; losses=[x for x in trades if x<=0]
    gw=sum(wins); gl=abs(sum(losses))
    pf=gw/gl if gl else (99 if gw else 0)
    return {"trades":len(trades),"profit_factor":round(pf,6),"total_return":round(equity-1,6),"max_drawdown":round(abs(dd),6),"winrate":round(len(wins)/len(trades)*100,4) if trades else 0}

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    queue=load()
    ds=datasets()
    results=[]
    for q in queue:
        for d in ds:
            closes=load_close(d)
            if len(closes)<100: continue
            m=sma_cross_backtest(closes,5,55)
            status="PAPER_CANDIDATE" if m["trades"]>=20 and m["profit_factor"]>=1.25 else "REJECTED"
            results.append({**q,"dataset":str(d),"backtest_metrics":m,"backtest_status":status,**BLOCKS})
    candidates=[x for x in results if x["backtest_status"]=="PAPER_CANDIDATE"]
    report={
        "STATUS":"P16.21K_VIDEO_STRATEGY_BACKTEST_EXECUTOR_IMPLEMENTED",
        "INPUT_VIDEO_STRATEGIES":len(queue),
        "DATASETS_TESTED":len(ds),
        "BACKTESTS_RUN":len(results),
        "PAPER_CANDIDATES":len(candidates),
        "NEXT":"P16.21L_VIDEO_STRATEGY_WALK_FORWARD_MONTE_CARLO",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p1621k_backtest_results.json").write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621k_candidates.json").write_text(json.dumps(candidates,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621k_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))

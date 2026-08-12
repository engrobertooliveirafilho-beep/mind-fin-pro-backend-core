import csv,json,statistics,random,subprocess,os,shutil
from pathlib import Path
from datetime import datetime,UTC

REMOTE_NORM="gdrive:mind-workspace/MIND_TRADER/P15_REAL_MARKET_DATA/normalized"
REMOTE_REPORTS="gdrive:mind-workspace/MIND_TRADER/P15_REAL_EDGE_RESEARCH/reports"
TMP=Path(os.environ.get("TEMP",".")).joinpath("mind_p15_edge_runtime")
DATA=TMP/"normalized"

FAST=[5,9,13]
SLOW=[21,34,55]
MIN_BARS=120

def cmd(c): return subprocess.run(c,shell=True,capture_output=True,text=True)

def f(v):
    try: return float(v)
    except: return 0.0

def load_csv(p):
    with open(p,newline="",encoding="utf-8") as fh:
        return [{**r,"close":f(r.get("close",0))} for r in csv.DictReader(fh) if f(r.get("close",0))>0]

def sma(vals,n,i):
    if i<n: return None
    return sum(vals[i-n:i])/n

def backtest(rows,fast,slow):
    closes=[r["close"] for r in rows]
    pos=0; entry=0; trades=[]
    for i in range(slow+1,len(closes)):
        f0=sma(closes,fast,i); s0=sma(closes,slow,i)
        f1=sma(closes,fast,i-1); s1=sma(closes,slow,i-1)
        if None in (f0,s0,f1,s1): continue
        if pos==0 and f0>s0 and f1<=s1:
            pos=1; entry=closes[i]
        elif pos==1 and f0<s0 and f1>=s1:
            trades.append((closes[i]/entry)-1); pos=0
    if pos==1: trades.append((closes[-1]/entry)-1)
    wins=[x for x in trades if x>0]; losses=[x for x in trades if x<=0]
    gross_win=sum(wins); gross_loss=abs(sum(losses))
    pf=(gross_win/gross_loss) if gross_loss>0 else (99 if gross_win>0 else 0)
    return {
        "trades":len(trades),
        "profit_factor":round(pf,4),
        "total_return":round(sum(trades),6),
        "winrate":round((len(wins)/len(trades))*100,2) if trades else 0,
        "avg_trade":round(statistics.mean(trades),6) if trades else 0,
        "trades_raw":trades
    }

def walk_forward(rows,fast,slow):
    n=len(rows)
    if n<MIN_BARS: return {"approved":False,"reason":"INSUFFICIENT_BARS"}
    a=backtest(rows[:int(n*.7)],fast,slow)
    b=backtest(rows[int(n*.7):],fast,slow)
    ok=a["profit_factor"]>=1.15 and b["profit_factor"]>=1.05 and a["trades"]>=5 and b["trades"]>=2
    return {"approved":ok,"train":a,"test":b}

def monte_carlo(trades):
    if len(trades)<10: return {"approved":False,"reason":"INSUFFICIENT_TRADES"}
    sims=[]
    for _ in range(100):
        t=trades[:]; random.shuffle(t); sims.append(sum(t))
    q10=sorted(sims)[10]
    return {"approved":q10>0,"q10_return":round(q10,6),"sims":100}

def run():
    if TMP.exists(): shutil.rmtree(TMP,ignore_errors=True)
    DATA.mkdir(parents=True,exist_ok=True)
    cmd(f'rclone copy "{REMOTE_NORM}" "{DATA}" --progress')

    results=[]
    for p in DATA.glob("*.csv"):
        rows=load_csv(p)
        if len(rows)<MIN_BARS: continue
        symbol=rows[0].get("symbol",p.stem)
        timeframe=rows[0].get("timeframe","")
        for fast in FAST:
            for slow in SLOW:
                if fast>=slow: continue
                bt=backtest(rows,fast,slow)
                wf=walk_forward(rows,fast,slow)
                mc=monte_carlo(bt["trades_raw"])
                promoted=bt["profit_factor"]>=1.25 and bt["trades"]>=10 and wf["approved"] and mc["approved"]
                results.append({
                    "dataset":p.name,"symbol":symbol,"timeframe":timeframe,
                    "strategy":"sma_cross","fast":fast,"slow":slow,
                    "profit_factor":bt["profit_factor"],"trades":bt["trades"],
                    "total_return":bt["total_return"],"winrate":bt["winrate"],
                    "walk_forward_approved":wf["approved"],
                    "monte_carlo_approved":mc["approved"],
                    "promoted":promoted,
                    "live":"FORBIDDEN","real_orders":"FORBIDDEN"
                })

    results.sort(key=lambda x:(x["promoted"],x["profit_factor"],x["total_return"]),reverse=True)
    promoted=[r for r in results if r["promoted"]]
    wf=[r for r in results if r["walk_forward_approved"]]
    mc=[r for r in results if r["monte_carlo_approved"]]

    out=Path("reports/P15.6_P15.10_REAL_EDGE_RESEARCH_RUNTIME")
    out.mkdir(parents=True,exist_ok=True)
    manifest={
        "STATUS":"P15.6_P15.10_REAL_EDGE_RESEARCH_RUNTIME_IMPLEMENTED",
        "DATASETS_TESTED":len(set(r["dataset"] for r in results)),
        "BACKTESTS_RUN":len(results),
        "WALK_FORWARD_APPROVED":len(wf),
        "MONTE_CARLO_APPROVED":len(mc),
        "PROMOTED":len(promoted),
        "EDGE":"CANDIDATE_FOUND" if promoted else "NOT_PROVEN",
        "LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN",
        "CAUSALITY":"NOT_PROVEN",
        "NEXT":"P15.11_PROMOTED_EDGE_FORENSIC_AUDIT",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"all_edge_research_results.json").write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"promoted_edges.json").write_text(json.dumps(promoted,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P15.6_P15.10_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    cmd(f'rclone copy "{out}" "{REMOTE_REPORTS}" --progress')
    shutil.rmtree(TMP,ignore_errors=True)
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))

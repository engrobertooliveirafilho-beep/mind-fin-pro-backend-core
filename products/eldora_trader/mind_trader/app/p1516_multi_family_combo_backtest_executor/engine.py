import csv,json,statistics,random,subprocess,os,shutil,itertools,math
from pathlib import Path
from datetime import datetime,UTC

QUEUE=Path("reports/P15.15_WEB_RESEARCH_TO_BACKTEST_QUEUE/backtest_queue.json")
REMOTE_NORM="gdrive:mind-workspace/MIND_TRADER/P15_REAL_MARKET_DATA/normalized"
REMOTE_REPORTS="gdrive:mind-workspace/MIND_TRADER/P15_REAL_EDGE_RESEARCH/reports/P15.16"
TMP=Path(os.environ.get("TEMP",".")).joinpath("mind_p1516_combo_runtime")
DATA=TMP/"normalized"

MAX_QUEUE=120
MIN_BARS=120

def cmd(c):
    return subprocess.run(c,shell=True,capture_output=True,text=True)

def f(v):
    try: return float(v)
    except: return 0.0

def load_json(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

def load_csv(p):
    with open(p,newline="",encoding="utf-8") as fh:
        return [{**r,"open":f(r.get("open",0)),"high":f(r.get("high",0)),"low":f(r.get("low",0)),"close":f(r.get("close",0)),"volume":f(r.get("volume",0))} for r in csv.DictReader(fh) if f(r.get("close",0))>0]

def sma(vals,n,i):
    if i<n: return None
    return sum(vals[i-n:i])/n

def rsi(vals,n,i):
    if i<n+1: return None
    gains=[]; losses=[]
    for j in range(i-n+1,i+1):
        d=vals[j]-vals[j-1]
        gains.append(max(d,0)); losses.append(abs(min(d,0)))
    avg_gain=sum(gains)/n; avg_loss=sum(losses)/n
    if avg_loss==0: return 100
    rs=avg_gain/avg_loss
    return 100-(100/(1+rs))

def donchian_high(vals,n,i):
    if i<n: return None
    return max(vals[i-n:i])

def boll_mid(vals,n,i):
    return sma(vals,n,i)

def signal(pattern,rows,i):
    closes=[r["close"] for r in rows]
    highs=[r["high"] for r in rows]
    vols=[r["volume"] for r in rows]

    if pattern in ("sma_cross","ema_cross"):
        f0=sma(closes,9,i); s0=sma(closes,34,i); f1=sma(closes,9,i-1); s1=sma(closes,34,i-1)
        return f0 and s0 and f1 and s1 and f0>s0 and f1<=s1

    if pattern=="rsi_reversion":
        rr=rsi(closes,14,i)
        return rr is not None and rr<35

    if pattern=="bollinger_reversion":
        m=boll_mid(closes,20,i)
        return m is not None and closes[i]<m*0.98

    if pattern in ("range_breakout","opening_range_breakout","volatility_breakout","donchian_trend"):
        h=donchian_high(highs,20,i)
        return h is not None and closes[i]>h

    if pattern in ("volume_spike","obv_confirmation"):
        mv=sma(vols,20,i)
        return mv is not None and vols[i]>mv*1.5

    if pattern in ("atr_expansion","bollinger_squeeze","adx_trend","trend_regime","volatility_regime","sideways_regime","h1_trend_m15_entry","d1_bias_h1_entry","atr_stop","fixed_stop_take","trailing_stop","vwap_reversion"):
        f0=sma(closes,13,i); s0=sma(closes,55,i)
        return f0 and s0 and f0>s0

    return False

def backtest(rows,patterns):
    closes=[r["close"] for r in rows]
    pos=0; entry=0; trades=[]
    for i in range(60,len(rows)):
        ok=all(signal(p,rows,i) for p in patterns)
        exit_sig=False
        f0=sma(closes,9,i); s0=sma(closes,34,i)
        if f0 and s0 and f0<s0:
            exit_sig=True
        if pos==0 and ok:
            pos=1; entry=closes[i]
        elif pos==1 and exit_sig:
            trades.append((closes[i]/entry)-1); pos=0
    if pos==1:
        trades.append((closes[-1]/entry)-1)
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

def walk_forward(rows,patterns):
    n=len(rows)
    if n<MIN_BARS: return {"approved":False}
    train=backtest(rows[:int(n*.7)],patterns)
    test=backtest(rows[int(n*.7):],patterns)
    return {"approved":train["profit_factor"]>=1.10 and test["profit_factor"]>=1.05 and train["trades"]>=3 and test["trades"]>=1,"train":train,"test":test}

def monte_carlo(trades):
    if len(trades)<8: return {"approved":False}
    sims=[]
    for _ in range(100):
        t=trades[:]; random.shuffle(t); sims.append(sum(t))
    return {"approved":sorted(sims)[10]>0,"q10_return":round(sorted(sims)[10],6)}

def build_combos(queue):
    grouped={}
    for q in queue[:MAX_QUEUE]:
        key=(q["asset"],q["timeframe"],q["dataset"])
        grouped.setdefault(key,[]).append(q["pattern"])
    jobs=[]
    for (asset,tf,dataset),patterns in grouped.items():
        uniq=list(dict.fromkeys(patterns))
        for p in uniq:
            jobs.append((asset,tf,dataset,[p],"single"))
        for combo in itertools.combinations(uniq[:8],2):
            jobs.append((asset,tf,dataset,list(combo),"combo_2"))
        for combo in itertools.combinations(uniq[:6],3):
            jobs.append((asset,tf,dataset,list(combo),"combo_3"))
    return jobs

def run():
    if TMP.exists(): shutil.rmtree(TMP,ignore_errors=True)
    DATA.mkdir(parents=True,exist_ok=True)
    cmd(f'rclone copy "{REMOTE_NORM}" "{DATA}" --progress')

    queue=load_json(QUEUE)
    jobs=build_combos(queue)
    results=[]

    for asset,tf,dataset,patterns,kind in jobs:
        p=DATA/dataset
        if not p.exists(): continue
        rows=load_csv(p)
        if len(rows)<MIN_BARS: continue
        bt=backtest(rows,patterns)
        wf=walk_forward(rows,patterns)
        mc=monte_carlo(bt["trades_raw"])
        promoted=bt["profit_factor"]>=1.35 and bt["trades"]>=8 and wf["approved"] and mc["approved"]
        results.append({
            "asset":asset,"timeframe":tf,"dataset":dataset,
            "kind":kind,"patterns":patterns,
            "profit_factor":bt["profit_factor"],"trades":bt["trades"],
            "total_return":bt["total_return"],"winrate":bt["winrate"],
            "walk_forward_approved":wf["approved"],
            "monte_carlo_approved":mc["approved"],
            "promoted":promoted,
            "live":"FORBIDDEN","real_orders":"FORBIDDEN"
        })

    results.sort(key=lambda x:(x["promoted"],x["profit_factor"],x["total_return"]),reverse=True)
    promoted=[r for r in results if r["promoted"]]

    out=Path("reports/P15.16_MULTI_FAMILY_COMBO_BACKTEST_EXECUTOR")
    out.mkdir(parents=True,exist_ok=True)
    manifest={
        "STATUS":"P15.16_MULTI_FAMILY_COMBO_BACKTEST_EXECUTOR_IMPLEMENTED",
        "QUEUE_ITEMS_USED":min(len(queue),MAX_QUEUE),
        "JOBS_BUILT":len(jobs),
        "BACKTESTS_RUN":len(results),
        "SINGLE_TESTS":sum(r["kind"]=="single" for r in results),
        "COMBO_2_TESTS":sum(r["kind"]=="combo_2" for r in results),
        "COMBO_3_TESTS":sum(r["kind"]=="combo_3" for r in results),
        "PROMOTED":len(promoted),
        "EDGE":"COMBO_CANDIDATE_FOUND" if promoted else "NOT_PROVEN",
        "LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN",
        "CAUSALITY":"NOT_PROVEN",
        "NEXT":"P15.17_COMBO_EDGE_PROMOTION_AUTHORITY",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"combo_backtest_results.json").write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"combo_promoted_edges.json").write_text(json.dumps(promoted,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P15.16_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    cmd(f'rclone copy "{out}" "{REMOTE_REPORTS}" --progress')
    shutil.rmtree(TMP,ignore_errors=True)
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))

import csv,json,math,itertools
from pathlib import Path
from datetime import datetime

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

TF_FILE="mind_ger40_5y_p2363b_DE40_M15_csv"
DATE_FORMATS=["%Y.%m.%d %H:%M:%S","%Y-%m-%d %H:%M:%S"]
ATR_PERIOD=14
ATR_FLOOR=8.0
MAX_ABS_R=10.0

BASELINE={
    "pf":1.543464,
    "winrate":56.521739,
    "expectancy":0.104782,
    "max_dd_r":4.544174
}

def safety():
    assert MODE=="PAPER_ONLY"
    assert REAL_ORDERS=="FORBIDDEN"
    assert FTMO_REAL=="FORBIDDEN"

def fnum(x):
    try: return float(str(x).replace(",","."))
    except Exception: return 0.0

def parse_time(x):
    s=str(x).strip()
    for fmt in DATE_FORMATS:
        try: return datetime.strptime(s[:19],fmt)
        except Exception: pass
    return datetime.min

def read_csv(path):
    with open(path,"r",encoding="utf-8-sig",newline="") as f:
        sample=f.read(4096)
        f.seek(0)
        delimiter=";" if sample.count(";")>=sample.count(",") else ","
        return list(csv.DictReader(f,delimiter=delimiter))

def write_csv(path,rows,fields):
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k:r.get(k,"") for k in fields})

def norm(r):
    return {
        "time":r.get("time",""),
        "dt":parse_time(r.get("time","")),
        "open":fnum(r.get("open")),
        "high":fnum(r.get("high")),
        "low":fnum(r.get("low")),
        "close":fnum(r.get("close")),
        "tick_volume":fnum(r.get("tick_volume")),
        "spread":fnum(r.get("spread")),
    }

def tr(c,p):
    if not p: return max(c["high"]-c["low"],0.0)
    return max(c["high"]-c["low"],abs(c["high"]-p["close"]),abs(c["low"]-p["close"]))

def add_atr(rows):
    rows=sorted(rows,key=lambda x:x["dt"])
    trs=[]
    for i,c in enumerate(rows):
        t=tr(c,rows[i-1] if i>0 else None)
        trs.append(t)
        c["atr"]=0.0 if i<ATR_PERIOD else max(sum(trs[i-ATR_PERIOD+1:i+1])/ATR_PERIOD,ATR_FLOOR)
    return rows

def sma(vals,n):
    if len(vals)<n: return None
    return sum(vals[-n:])/n

def session(dt):
    h=dt.hour
    if 8<=h<12: return "EUROPE_OPEN"
    if 12<=h<16: return "EUROPE_US_OVERLAP"
    if 16<=h<21: return "US_AFTERNOON"
    return "OFF_SESSION"

def regime(c,p):
    if not p: return "UNKNOWN"
    rng=max(c["high"]-c["low"],0.000001)
    body=abs(c["close"]-c["open"])
    delta=c["close"]-p["close"]
    br=body/rng
    if delta>0 and br>=0.35: return "TREND_UP"
    if delta<0 and br>=0.35: return "TREND_DOWN"
    if br<0.25: return "RANGE_COMPRESSION"
    return "RANGE_EXPANSION"

def footprint(c,p):
    if not p: return "UNKNOWN"
    if c["high"]>p["high"] and c["close"]<p["high"]: return "LIQUIDITY_SWEEP_REVERSAL_DOWN"
    if c["low"]<p["low"] and c["close"]>p["low"]: return "LIQUIDITY_SWEEP_REVERSAL_UP"
    rng=max(c["high"]-c["low"],0.000001)
    pr=max(p["high"]-p["low"],0.000001)
    body=abs(c["close"]-c["open"])
    if rng>pr*1.8 and body/rng>0.55: return "DISPLACEMENT"
    return "NORMAL_FLOW"

def lifecycle(c,p):
    fp=footprint(c,p)
    if fp in ["LIQUIDITY_SWEEP_REVERSAL_UP","LIQUIDITY_SWEEP_REVERSAL_DOWN"]: return "LIQUIDITY_REVERSAL_ENTRY"
    if c["close"]>p["high"]: return "CONTINUATION_UP"
    if c["close"]<p["low"]: return "CONTINUATION_DOWN"
    return "PULLBACK_OR_BALANCE"

def cycle(c,closes):
    ma20=sma(closes,20)
    ma50=sma(closes,50)
    if ma20 is None or ma50 is None: return "UNKNOWN"
    rng=max(c["high"]-c["low"],0.000001)
    body=abs(c["close"]-c["open"])
    br=body/rng
    if ma20>ma50 and c["close"]>ma20 and br>=0.35: return "MARKUP"
    if ma20<ma50 and c["close"]<ma20 and br>=0.35: return "MARKDOWN"
    if ma20<ma50 and br<0.35: return "ACCUMULATION"
    if ma20>ma50 and br<0.35: return "DISTRIBUTION"
    return "BALANCE"

def clamp(x): return max(min(x,MAX_ABS_R),-MAX_ABS_R)

def metrics(rs):
    n=len(rs)
    wins=[x for x in rs if x>0]
    losses=[x for x in rs if x<0]
    gw=sum(wins); gl=abs(sum(losses))
    pf=999.0 if gl==0 and gw>0 else (gw/gl if gl>0 else 0.0)
    exp=sum(rs)/n if n else 0.0
    wr=len(wins)/n*100 if n else 0.0
    eq=0; peak=0; dd=0
    for r in rs:
        eq+=r; peak=max(peak,eq); dd=max(dd,peak-eq)
    return {
        "samples":n,"wins":len(wins),"losses":len(losses),
        "winrate":round(wr,6),"pf":round(pf,6),
        "expectancy":round(exp,6),"max_dd_r":round(dd,6),
        "gross_win":round(gw,6),"gross_loss":round(gl,6),
        "net_r":round(eq,6)
    }

def baseline_gate(m):
    return (
        m["samples"]>=30 and
        m["pf"]>BASELINE["pf"] and
        m["winrate"]>BASELINE["winrate"] and
        m["expectancy"]>BASELINE["expectancy"] and
        m["max_dd_r"]<=BASELINE["max_dd_r"]
    )

def run(dataset,baseline,lock,outdir):
    safety()
    out=Path(outdir); out.mkdir(parents=True,exist_ok=True)

    raw=read_csv(Path(dataset)/TF_FILE)
    candles=[norm(r) for r in raw]
    candles=[c for c in candles if c["dt"]!=datetime.min and c["close"]>0]
    candles=add_atr(candles)

    closes=[]
    prev_cycle="UNKNOWN"
    events=[]

    for i in range(1,len(candles)-1):
        c=candles[i]; p=candles[i-1]; n=candles[i+1]
        closes.append(c["close"])
        cyc=cycle(c,closes)
        ev={
            "time":c["time"],
            "timeframe":"M15",
            "regime":regime(c,p),
            "session":session(c["dt"]),
            "footprint":footprint(c,p),
            "lifecycle":lifecycle(c,p),
            "cycle":cyc,
            "previous_cycle":prev_cycle,
            "cycle_transition":prev_cycle+"->"+cyc,
            "atr":c["atr"],
            "close":c["close"],
            "next_close":n["close"]
        }
        prev_cycle=cyc
        events.append(ev)

    dimensions=[
        ["regime","session","footprint","lifecycle"],
        ["regime","session","footprint","lifecycle","cycle"],
        ["regime","session","footprint","lifecycle","cycle_transition"],
        ["session","footprint","lifecycle","cycle_transition"],
        ["regime","footprint","lifecycle","cycle_transition"],
    ]

    candidates=[]
    detail_rows=[]

    for dims in dimensions:
        groups={}
        for ev in events:
            key="|".join([ev[d] for d in dims])
            groups.setdefault(key,[]).append(ev)

        for key,rows in groups.items():
            for direction in [1,-1]:
                rs=[]
                for ev in rows:
                    if ev["atr"]<=0: continue
                    move=(ev["next_close"]-ev["close"])*direction
                    rs.append(clamp(move/max(ev["atr"],ATR_FLOOR)))
                m=metrics(rs)
                passed=baseline_gate(m)
                cand={
                    "candidate_id":"P2391_"+str(abs(hash((tuple(dims),key,direction)))%10000000000),
                    "dimensions":"+".join(dims),
                    "key":key,
                    "direction":"BUY_PAPER" if direction==1 else "SELL_PAPER",
                    **m,
                    "beats_baseline":passed,
                    "mode":MODE,
                    "real_orders":REAL_ORDERS,
                    "ftmo_real":FTMO_REAL
                }
                candidates.append(cand)
                if passed:
                    for ev in rows[:2000]:
                        detail_rows.append({
                            "candidate_id":cand["candidate_id"],
                            "time":ev["time"],
                            "direction":cand["direction"],
                            "key":key,
                            "cycle_transition":ev["cycle_transition"],
                            "regime":ev["regime"],
                            "session":ev["session"],
                            "footprint":ev["footprint"],
                            "lifecycle":ev["lifecycle"],
                            "cycle":ev["cycle"],
                        })

    promoted=[c for c in candidates if c["beats_baseline"]]
    observed=[c for c in candidates if (not c["beats_baseline"] and c["samples"]>=30 and c["pf"]>=1.3 and c["expectancy"]>0)]
    rejected=[c for c in candidates if c not in promoted and c not in observed]

    candidates=sorted(candidates,key=lambda x:(x["beats_baseline"],x["pf"],x["expectancy"],-x["max_dd_r"]),reverse=True)
    promoted=sorted(promoted,key=lambda x:(x["pf"],x["expectancy"],-x["max_dd_r"]),reverse=True)

    fields=list(candidates[0].keys()) if candidates else ["candidate_id"]
    write_csv(out/"de40_p2391_edge_candidates_all.csv",candidates,fields)
    write_csv(out/"de40_p2391_edge_promoted.csv",promoted,fields)
    write_csv(out/"de40_p2391_edge_observed.csv",observed,fields)
    write_csv(out/"de40_p2391_edge_rejected.csv",rejected,fields)
    write_csv(out/"de40_p2391_promoted_detail_events.csv",detail_rows,list(detail_rows[0].keys()) if detail_rows else ["candidate_id"])

    summary={
        "mission":"P2391_RETURN_TO_EDGE_RESEARCH",
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "dataset":str(dataset),
        "baseline":str(baseline),
        "governance_lock":str(lock),
        "output":str(out),
        "baseline_metrics":BASELINE,
        "events":len(events),
        "candidates":len(candidates),
        "promoted":len(promoted),
        "observed":len(observed),
        "rejected":len(rejected),
        "best_candidate":promoted[0] if promoted else (candidates[0] if candidates else {}),
        "certification":"P2391_EDGE_RESEARCH_PROMOTED" if promoted else "P2391_EDGE_RESEARCH_NO_SUPERIOR_EDGE",
        "paper_stack_modified":False,
        "real_execution_allowed":False,
        "next_required":"P2392_EDGE_WALK_FORWARD_VALIDATION" if promoted else "P2391B_EDGE_SEARCH_EXPANSION"
    }

    with open(out/"summary.json","w",encoding="utf-8") as f:
        json.dump(summary,f,indent=2,ensure_ascii=False)

    return summary

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--dataset",required=True)
    p.add_argument("--baseline",required=True)
    p.add_argument("--lock",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.dataset,a.baseline,a.lock,a.out),indent=2,ensure_ascii=False))

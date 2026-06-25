import csv,json,math
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
WINDOWS=5

CRITERIA={
    "pf":1.50,
    "winrate":45.0,
    "expectancy":0.0,
    "samples":30,
    "passed_windows":4
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
    if fp in ["LIQUIDITY_SWEEP_REVERSAL_UP","LIQUIDITY_SWEEP_REVERSAL_DOWN"]:
        return "LIQUIDITY_REVERSAL_ENTRY"
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

def clamp(x):
    return max(min(x,MAX_ABS_R),-MAX_ABS_R)

def metrics(rs):
    n=len(rs)
    wins=[x for x in rs if x>0]
    losses=[x for x in rs if x<0]
    gw=sum(wins)
    gl=abs(sum(losses))
    pf=999.0 if gl==0 and gw>0 else (gw/gl if gl>0 else 0.0)
    exp=sum(rs)/n if n else 0.0
    wr=len(wins)/n*100 if n else 0.0
    eq=0
    peak=0
    dd=0
    for r in rs:
        eq+=r
        peak=max(peak,eq)
        dd=max(dd,peak-eq)
    return {
        "samples":n,
        "wins":len(wins),
        "losses":len(losses),
        "winrate":round(wr,6),
        "pf":round(pf,6),
        "expectancy":round(exp,6),
        "max_dd_r":round(dd,6),
        "gross_win":round(gw,6),
        "gross_loss":round(gl,6),
        "net_r":round(eq,6)
    }

def pass_gate(m):
    return (
        m["samples"]>=CRITERIA["samples"] and
        m["pf"]>=CRITERIA["pf"] and
        m["winrate"]>=CRITERIA["winrate"] and
        m["expectancy"]>CRITERIA["expectancy"]
    )

def build_events(dataset):
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
            "dt":c["dt"],
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
    return events

def candidate_match(ev,c):
    dims=c["dimensions"].split("+")
    vals=c["key"].split("|")
    for d,v in zip(dims,vals):
        if ev.get(d,"") != v:
            return False
    return True

def run(dataset,p2391,lock,outdir):
    safety()
    out=Path(outdir)
    out.mkdir(parents=True,exist_ok=True)

    events=build_events(dataset)
    promoted_in=read_csv(Path(p2391)/"de40_p2391_edge_promoted.csv")

    results=[]
    detail=[]
    stability=[]

    for c in promoted_in:
        cand_id=c["candidate_id"]
        direction=1 if c["direction"]=="BUY_PAPER" else -1
        matched=[ev for ev in events if candidate_match(ev,c)]
        matched=sorted(matched,key=lambda x:x["dt"])

        if len(matched)==0:
            continue

        chunk=max(1,math.floor(len(matched)/WINDOWS))
        passed_windows=0
        window_metrics=[]

        for w in range(WINDOWS):
            start=w*chunk
            end=(w+1)*chunk if w<WINDOWS-1 else len(matched)
            win_events=matched[start:end]
            rs=[]
            for ev in win_events:
                if ev["atr"]<=0:
                    continue
                rr=clamp((ev["next_close"]-ev["close"])*direction/max(ev["atr"],ATR_FLOOR))
                rs.append(rr)
                detail.append({
                    "candidate_id":cand_id,
                    "window":w+1,
                    "time":ev["time"],
                    "direction":c["direction"],
                    "realized_r":round(rr,6),
                    "key":c["key"],
                    "dimensions":c["dimensions"],
                    "mode":MODE,
                    "real_orders":REAL_ORDERS,
                    "ftmo_real":FTMO_REAL
                })

            m=metrics(rs)
            passed=pass_gate(m)
            if passed:
                passed_windows+=1

            row={
                "candidate_id":cand_id,
                "window":w+1,
                "window_start":win_events[0]["time"] if win_events else "",
                "window_end":win_events[-1]["time"] if win_events else "",
                **m,
                "passed":passed
            }
            window_metrics.append(row)
            stability.append(row)

        all_rs=[]
        for ev in matched:
            if ev["atr"]<=0:
                continue
            all_rs.append(clamp((ev["next_close"]-ev["close"])*direction/max(ev["atr"],ATR_FLOOR)))
        total=metrics(all_rs)

        decision="REJECT"
        if passed_windows>=4:
            decision="PROMOTE"
        elif passed_windows==3:
            decision="OBSERVE"

        results.append({
            "candidate_id":cand_id,
            "dimensions":c["dimensions"],
            "key":c["key"],
            "direction":c["direction"],
            "matched_events":len(matched),
            "passed_windows":passed_windows,
            "decision":decision,
            **total,
            "mode":MODE,
            "real_orders":REAL_ORDERS,
            "ftmo_real":FTMO_REAL
        })

    promoted=[r for r in results if r["decision"]=="PROMOTE"]
    observed=[r for r in results if r["decision"]=="OBSERVE"]
    rejected=[r for r in results if r["decision"]=="REJECT"]

    fields=list(results[0].keys()) if results else ["candidate_id"]
    write_csv(out/"de40_edge_walkforward_results.csv",results,fields)
    write_csv(out/"de40_edge_promoted.csv",promoted,fields)
    write_csv(out/"de40_edge_observed.csv",observed,fields)
    write_csv(out/"de40_edge_rejected.csv",rejected,fields)
    write_csv(out/"de40_edge_stability.csv",stability,list(stability[0].keys()) if stability else ["candidate_id"])
    write_csv(out/"de40_edge_walkforward_detail.csv",detail,list(detail[0].keys()) if detail else ["candidate_id"])

    summary={
        "mission":"P2392_EDGE_WALK_FORWARD_VALIDATION",
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "dataset":str(dataset),
        "p2391":str(p2391),
        "governance_lock":str(lock),
        "output":str(out),
        "windows":WINDOWS,
        "criteria":CRITERIA,
        "input_candidates":len(promoted_in),
        "tested":len(results),
        "promoted":len(promoted),
        "observed":len(observed),
        "rejected":len(rejected),
        "best_promoted":promoted[0] if promoted else {},
        "paper_stack_modified":False,
        "real_execution_allowed":False,
        "certification":"P2392_EDGE_WALK_FORWARD_PROMOTED" if promoted else "P2392_EDGE_WALK_FORWARD_NO_PROMOTION",
        "next_required":"P2393_EDGE_CLUSTERING" if promoted else "P2392B_EDGE_SEARCH_REPAIR"
    }

    with open(out/"summary.json","w",encoding="utf-8") as f:
        json.dump(summary,f,indent=2,ensure_ascii=False)

    return summary

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--dataset",required=True)
    p.add_argument("--p2391",required=True)
    p.add_argument("--lock",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.dataset,a.p2391,a.lock,a.out),indent=2,ensure_ascii=False))

import csv, json, math
from pathlib import Path
from datetime import datetime
from collections import defaultdict

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

TF_FILE="mind_ger40_5y_p2363b_DE40_M15_csv"
DATE_FORMATS=["%Y.%m.%d %H:%M:%S","%Y-%m-%d %H:%M:%S","%Y-%m-%dT%H:%M:%S"]
ATR_PERIOD=14
ATR_FLOOR=8.0
MAX_ABS_R=10.0

SURVIVOR={
    "timeframe":"M15",
    "regime":"TREND_DOWN",
    "session":"OFF_SESSION",
    "footprint":"LIQUIDITY_SWEEP_REVERSAL_UP",
    "lifecycle":"LIQUIDITY_REVERSAL_ENTRY",
}

def safety():
    assert MODE=="PAPER_ONLY"
    assert REAL_ORDERS=="FORBIDDEN"
    assert FTMO_REAL=="FORBIDDEN"

def fnum(x):
    try:
        return float(str(x).replace(",","."))
    except Exception:
        return 0.0

def parse_time(x):
    s=str(x).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s[:19],fmt)
        except Exception:
            pass
    return datetime.min

def read_csv(path):
    with open(path,"r",encoding="utf-8-sig",newline="") as f:
        sample=f.read(4096)
        f.seek(0)
        delimiter=";" if sample.count(";")>=sample.count(",") else ","
        return list(csv.DictReader(f,delimiter=delimiter))

def write_csv(path, rows, fields):
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
        "timeframe":r.get("timeframe","M15")
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

def sma(vals, n):
    if len(vals)<n: return None
    return sum(vals[-n:])/n

def session(dt):
    h=dt.hour
    if 8 <= h < 12: return "EUROPE_OPEN"
    if 12 <= h < 16: return "EUROPE_US_OVERLAP"
    if 16 <= h < 21: return "US_AFTERNOON"
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
    if c["high"]>p["high"] and c["close"]<p["high"]:
        return "LIQUIDITY_SWEEP_REVERSAL_DOWN"
    if c["low"]<p["low"] and c["close"]>p["low"]:
        return "LIQUIDITY_SWEEP_REVERSAL_UP"
    rng=max(c["high"]-c["low"],0.000001)
    pr=max(p["high"]-p["low"],0.000001)
    body=abs(c["close"]-c["open"])
    if rng>pr*1.8 and body/rng>0.55:
        return "DISPLACEMENT"
    return "NORMAL_FLOW"

def lifecycle(c,p):
    fp=footprint(c,p)
    if fp in ["LIQUIDITY_SWEEP_REVERSAL_UP","LIQUIDITY_SWEEP_REVERSAL_DOWN"]:
        return "LIQUIDITY_REVERSAL_ENTRY"
    if c["close"]>p["high"]: return "CONTINUATION_UP"
    if c["close"]<p["low"]: return "CONTINUATION_DOWN"
    return "PULLBACK_OR_BALANCE"

def cycle_class(c, closes, atrs):
    ma20=sma(closes,20)
    ma50=sma(closes,50)
    if ma20 is None or ma50 is None:
        return "UNKNOWN"

    rng=max(c["high"]-c["low"],0.000001)
    body=abs(c["close"]-c["open"])
    br=body/rng
    atr=c.get("atr",0.0)

    if ma20>ma50 and c["close"]>ma20 and br>=0.35:
        return "MARKUP"
    if ma20<ma50 and c["close"]<ma20 and br>=0.35:
        return "MARKDOWN"
    if ma20<ma50 and br<0.35:
        return "ACCUMULATION"
    if ma20>ma50 and br<0.35:
        return "DISTRIBUTION"
    return "BALANCE"

def clamp(x):
    return max(min(x,MAX_ABS_R),-MAX_ABS_R)

def metrics(rows):
    rs=[fnum(r.get("realized_r")) for r in rows]
    n=len(rs)
    wins=[x for x in rs if x>0]
    losses=[x for x in rs if x<0]
    gw=sum(wins)
    gl=abs(sum(losses))
    pf=999.0 if gl==0 and gw>0 else (gw/gl if gl>0 else 0.0)
    exp=sum(rs)/n if n else 0.0
    wr=len(wins)/n*100 if n else 0.0
    eq=0.0; peak=0.0; dd=0.0
    for r in rs:
        eq+=r; peak=max(peak,eq); dd=max(dd,peak-eq)
    return {"samples":n,"wins":len(wins),"losses":len(losses),"winrate":round(wr,6),"pf":round(pf,6),"expectancy":round(exp,6),"max_dd_r":round(dd,6),"gross_win":round(gw,6),"gross_loss":round(gl,6)}

def gate(m):
    return m["samples"]>=30 and m["pf"]>=1.5 and m["expectancy"]>0 and m["winrate"]>=45

def run(dataset,p2383d,outdir):
    safety()
    out=Path(outdir); out.mkdir(parents=True,exist_ok=True)

    raw=read_csv(Path(dataset)/TF_FILE)
    candles=[norm(r) for r in raw]
    candles=[c for c in candles if c["dt"]!=datetime.min and c["close"]>0]
    candles=add_atr(candles)

    closes=[]
    events=[]
    matches=[]
    transitions=[]

    prev_cycle="UNKNOWN"

    for i in range(1,len(candles)-1):
        c=candles[i]; p=candles[i-1]; n=candles[i+1]
        closes.append(c["close"])
        cyc=cycle_class(c,closes,[x.get("atr",0) for x in candles[max(0,i-50):i+1]])
        reg=regime(c,p)
        ses=session(c["dt"])
        fp=footprint(c,p)
        life=lifecycle(c,p)

        ev={
            "time":c["time"],
            "cycle":cyc,
            "previous_cycle":prev_cycle,
            "cycle_transition":prev_cycle+"->"+cyc,
            "timeframe":"M15",
            "regime":reg,
            "session":ses,
            "footprint":fp,
            "lifecycle":life,
            "atr":round(c["atr"],6),
            "close":c["close"]
        }
        events.append(ev)
        transitions.append({"from_cycle":prev_cycle,"to_cycle":cyc,"transition":prev_cycle+"->"+cyc})
        prev_cycle=cyc

        is_survivor=(
            reg==SURVIVOR["regime"] and
            ses==SURVIVOR["session"] and
            fp==SURVIVOR["footprint"] and
            life==SURVIVOR["lifecycle"]
        )

        if is_survivor and c["atr"]>0:
            direction=1
            rr=clamp((n["close"]-c["close"])/max(c["atr"],ATR_FLOOR))
            matches.append({
                **ev,
                "direction":"BUY",
                "next_close":n["close"],
                "realized_r":round(rr,6),
                "mode":MODE,
                "real_orders":REAL_ORDERS,
                "ftmo_real":FTMO_REAL
            })

    by_cycle=[]
    d=defaultdict(list)
    for m in matches:
        d[m["cycle"]].append(m)
    for cyc,rows in sorted(d.items()):
        mm=metrics(rows)
        by_cycle.append({"cycle":cyc,**mm,"passed":gate(mm)})

    by_transition=[]
    d=defaultdict(list)
    for m in matches:
        d[m["cycle_transition"]].append(m)
    for trn,rows in sorted(d.items()):
        mm=metrics(rows)
        by_transition.append({"cycle_transition":trn,**mm,"passed":gate(mm)})

    trans_count=defaultdict(int)
    for t in transitions:
        trans_count[t["transition"]]+=1
    transition_matrix=[{"transition":k,"count":v} for k,v in sorted(trans_count.items())]

    promoted=[r for r in by_cycle if r["passed"]]
    rejected=[r for r in by_cycle if not r["passed"]]
    global_m=metrics(matches)

    write_csv(out/"de40_cycle_events.csv",events,list(events[0].keys()))
    write_csv(out/"de40_cycle_survivor_matches.csv",matches,list(matches[0].keys()) if matches else ["time"])
    write_csv(out/"de40_cycle_playbook_results.csv",by_cycle,list(by_cycle[0].keys()) if by_cycle else ["cycle"])
    write_csv(out/"de40_cycle_transition_results.csv",by_transition,list(by_transition[0].keys()) if by_transition else ["cycle_transition"])
    write_csv(out/"de40_cycle_transition_matrix.csv",transition_matrix,list(transition_matrix[0].keys()))
    write_csv(out/"de40_cycle_promoted.csv",promoted,list(by_cycle[0].keys()) if by_cycle else ["cycle"])
    write_csv(out/"de40_cycle_rejected.csv",rejected,list(by_cycle[0].keys()) if by_cycle else ["cycle"])

    summary={
        "mission":"P2384_DE40_INSTITUTIONAL_CYCLE_ENGINE",
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "dataset":str(dataset),
        "p2383d":str(p2383d),
        "output":str(out),
        "survivor_context":SURVIVOR,
        "method":"Classify M15 raw candles into institutional cycles and measure survivor context by cycle/transition.",
        "events":len(events),
        "survivor_matches":len(matches),
        "global_metrics":global_m,
        "cycles_tested":len(by_cycle),
        "promoted":len(promoted),
        "rejected":len(rejected),
        "certification":"CYCLE_CONTEXT_PROMOTED" if len(promoted)>0 else "CYCLE_CONTEXT_NOT_PROMOTED",
        "p2385_allowed":True if len(promoted)>0 else False,
        "next_required":"P2385_DE40_SURVIVOR_CONTEXT_EXECUTION_FILTER" if len(promoted)>0 else "P2384B_CYCLE_CLASSIFIER_REPAIR"
    }

    with open(out/"summary.json","w",encoding="utf-8") as f:
        json.dump(summary,f,indent=2,ensure_ascii=False)

    return summary

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--dataset",required=True)
    p.add_argument("--p2383d",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.dataset,a.p2383d,a.out),indent=2,ensure_ascii=False))

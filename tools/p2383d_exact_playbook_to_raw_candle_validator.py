import csv, json, math
from pathlib import Path
from datetime import datetime
from collections import defaultdict

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

TIMEFRAME_FILES={
    "M1":"mind_ger40_5y_p2363b_DE40_M1_csv",
    "M5":"mind_ger40_5y_p2363b_DE40_M5_csv",
    "M15":"mind_ger40_5y_p2363b_DE40_M15_csv",
    "M30":"mind_ger40_5y_p2363b_DE40_M30_csv",
    "H1":"mind_ger40_5y_p2363b_DE40_H1_csv",
    "H4":"mind_ger40_5y_p2363b_DE40_H4_csv",
    "D1":"mind_ger40_5y_p2363b_DE40_D1_csv",
}

DATE_FORMATS=[
    "%Y.%m.%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y",
]

ATR_PERIOD=14
MAX_ABS_R=10.0

ATR_FLOOR={
    "M1":2.0,
    "M5":4.0,
    "M15":8.0,
    "M30":12.0,
    "H1":18.0,
    "H4":35.0,
    "D1":80.0,
}

PROMOTE={
    "pf":1.5,
    "expectancy":0.0,
    "winrate":45.0,
    "samples":30,
    "matched_oos_events":30
}

def safety():
    assert MODE=="PAPER_ONLY"
    assert REAL_ORDERS=="FORBIDDEN"
    assert FTMO_REAL=="FORBIDDEN"

def fnum(x):
    try:
        if x is None or str(x).strip()=="":
            return 0.0
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

def read_csv_auto(path):
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

def normalize_candle(row):
    return {
        "time":row.get("time",""),
        "dt":parse_time(row.get("time","")),
        "open":fnum(row.get("open")),
        "high":fnum(row.get("high")),
        "low":fnum(row.get("low")),
        "close":fnum(row.get("close")),
        "tick_volume":fnum(row.get("tick_volume")),
        "spread":fnum(row.get("spread")),
        "symbol":row.get("symbol","DE40"),
        "timeframe":row.get("timeframe","")
    }

def true_range(c, prev):
    if not prev:
        return max(c["high"]-c["low"],0.0)
    return max(c["high"]-c["low"], abs(c["high"]-prev["close"]), abs(c["low"]-prev["close"]))

def add_atr(rows, tf):
    rows=sorted(rows,key=lambda x:x["dt"])
    trs=[]
    for i,c in enumerate(rows):
        prev=rows[i-1] if i>0 else None
        tr=true_range(c,prev)
        trs.append(tr)
        if i < ATR_PERIOD:
            c["atr"]=0.0
        else:
            raw=sum(trs[i-ATR_PERIOD+1:i+1])/ATR_PERIOD
            c["atr"]=max(raw, ATR_FLOOR.get(tf,1.0))
    return rows

def split_oos(rows):
    rows=sorted(rows,key=lambda x:x["dt"])
    cut=math.floor(len(rows)*0.80)
    return rows[:cut], rows[cut:]

def session(dt):
    h=dt.hour
    if 1 <= h < 8:
        return "ASIA_EARLY_EUROPE"
    if 8 <= h < 12:
        return "EUROPE_OPEN"
    if 12 <= h < 16:
        return "EUROPE_US_OVERLAP"
    if 16 <= h < 21:
        return "US_AFTERNOON"
    return "OFF_SESSION"

def regime(c, prev):
    if not prev:
        return "UNKNOWN"
    lookback_delta=c["close"]-prev["close"]
    rng=max(c["high"]-c["low"],0.000001)
    body=abs(c["close"]-c["open"])
    body_ratio=body/rng

    if lookback_delta > 0 and body_ratio >= 0.35:
        return "TREND_UP"
    if lookback_delta < 0 and body_ratio >= 0.35:
        return "TREND_DOWN"
    if body_ratio < 0.25:
        return "RANGE_COMPRESSION"
    return "RANGE_EXPANSION"

def footprint(c, prev):
    if not prev:
        return "UNKNOWN"

    if c["high"] > prev["high"] and c["close"] < prev["high"]:
        return "LIQUIDITY_SWEEP_REVERSAL_DOWN"

    if c["low"] < prev["low"] and c["close"] > prev["low"]:
        return "LIQUIDITY_SWEEP_REVERSAL_UP"

    rng=max(c["high"]-c["low"],0.000001)
    prev_rng=max(prev["high"]-prev["low"],0.000001)
    body=abs(c["close"]-c["open"])

    if rng > prev_rng*1.8 and body/rng > 0.55:
        return "DISPLACEMENT"

    return "NORMAL_FLOW"

def lifecycle(c, prev):
    if not prev:
        return "UNKNOWN"

    fp=footprint(c,prev)
    if fp in ["LIQUIDITY_SWEEP_REVERSAL_UP","LIQUIDITY_SWEEP_REVERSAL_DOWN"]:
        return "LIQUIDITY_REVERSAL_ENTRY"

    if c["close"] > prev["high"]:
        return "CONTINUATION_UP"

    if c["close"] < prev["low"]:
        return "CONTINUATION_DOWN"

    return "PULLBACK_OR_BALANCE"

def clamp(x):
    return max(min(x,MAX_ABS_R),-MAX_ABS_R)

def direction_for_playbook(pb):
    fp=pb.get("footprint","")
    direction=pb.get("direction","")
    if direction=="BUY_PAPER":
        return 1
    if direction=="SELL_PAPER":
        return -1
    if fp=="LIQUIDITY_SWEEP_REVERSAL_UP":
        return 1
    if fp=="LIQUIDITY_SWEEP_REVERSAL_DOWN":
        return -1
    return 1

def metrics(rows):
    n=len(rows)
    rs=[fnum(r.get("realized_r")) for r in rows]
    wins=[x for x in rs if x>0]
    losses=[x for x in rs if x<0]
    gw=sum(wins)
    gl=abs(sum(losses))
    pf=999.0 if gl==0 and gw>0 else (gw/gl if gl>0 else 0.0)
    exp=sum(rs)/n if n else 0.0
    wr=len(wins)/n*100.0 if n else 0.0
    eq=0.0
    peak=0.0
    dd=0.0
    for r in rs:
        eq += r
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
        "gross_loss":round(gl,6)
    }

def gate(m):
    return m["samples"]>=PROMOTE["samples"] and m["pf"]>=PROMOTE["pf"] and m["expectancy"]>PROMOTE["expectancy"] and m["winrate"]>=PROMOTE["winrate"]

def playbook_key(r):
    return "|".join([
        r.get("timeframe",""),
        r.get("regime",""),
        r.get("session",""),
        r.get("footprint",""),
        r.get("lifecycle",""),
    ])

def candle_key(ev):
    return "|".join([
        ev.get("timeframe",""),
        ev.get("regime",""),
        ev.get("session",""),
        ev.get("footprint",""),
        ev.get("lifecycle",""),
    ])

def build_event(c, prev, nxt, tf):
    if not prev or not nxt:
        return None
    if c.get("atr",0.0)<=0:
        return None
    if c["high"]-c["low"]<=0:
        return None

    return {
        "entry_time":c["time"],
        "timeframe":tf,
        "regime":regime(c,prev),
        "session":session(c["dt"]),
        "footprint":footprint(c,prev),
        "lifecycle":lifecycle(c,prev),
        "open":c["open"],
        "high":c["high"],
        "low":c["low"],
        "close":c["close"],
        "next_close":nxt["close"],
        "atr":c["atr"],
    }

def simulate_match(event, pb):
    direction=direction_for_playbook(pb)
    move=(event["next_close"]-event["close"])*direction
    r=clamp(move/max(event["atr"],ATR_FLOOR.get(event["timeframe"],1.0)))
    return {
        "entry_time":event["entry_time"],
        "symbol":"DE40",
        "timeframe":event["timeframe"],
        "playbook_id":pb.get("playbook_id",pb.get("signal_id","")),
        "family":pb.get("family",""),
        "regime":event["regime"],
        "session":event["session"],
        "footprint":event["footprint"],
        "lifecycle":event["lifecycle"],
        "direction":"BUY" if direction==1 else "SELL",
        "atr":round(event["atr"],6),
        "entry_close":event["close"],
        "next_close":event["next_close"],
        "realized_r":round(r,6),
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "warning":"PAPER_ONLY_VALIDATION_NOT_REAL_ORDER"
    }

def run(dataset,p2378,p2379,p2383c2,outdir):
    safety()
    out=Path(outdir)
    out.mkdir(parents=True,exist_ok=True)

    pb_path=Path(p2378)/"de40_promoted_playbooks.csv"
    bus_path=Path(p2379)/"mind_de40_paper_signal_bus_p2379.csv"

    if not pb_path.exists():
        raise FileNotFoundError(str(pb_path))
    if not bus_path.exists():
        raise FileNotFoundError(str(bus_path))

    promoted_playbooks=read_csv_auto(pb_path)
    signal_bus=read_csv_auto(bus_path)

    # Use promoted playbooks as source of truth; enrich with bus direction when same contextual key exists.
    bus_by_key=defaultdict(list)
    for s in signal_bus:
        bus_by_key[playbook_key(s)].append(s)

    playbooks=[]
    for pb in promoted_playbooks:
        if pb.get("mode")!="PAPER_ONLY":
            continue
        if pb.get("real_orders")!="FORBIDDEN":
            continue
        if pb.get("ftmo_real")!="FORBIDDEN":
            continue

        k=playbook_key(pb)
        enriched=dict(pb)
        if bus_by_key.get(k):
            enriched["direction"]=bus_by_key[k][0].get("direction","")
            enriched["signal_status"]=bus_by_key[k][0].get("signal_status","")
        else:
            enriched["direction"]=""
            enriched["signal_status"]="NO_BUS_MATCH"
        enriched["context_key"]=k
        playbooks.append(enriched)

    playbook_index=defaultdict(list)
    for pb in playbooks:
        playbook_index[pb["context_key"]].append(pb)

    all_events=[]
    all_matches=[]
    tf_audit=[]

    for tf,file in TIMEFRAME_FILES.items():
        path=Path(dataset)/file
        raw=read_csv_auto(path)
        candles=[normalize_candle(r) for r in raw]
        candles=[c for c in candles if c["dt"]!=datetime.min and c["open"]>0 and c["high"]>0 and c["low"]>0 and c["close"]>0]
        candles=add_atr(candles,tf)
        train,oos=split_oos(candles)

        events=[]
        matches=[]
        for i in range(1,len(oos)-1):
            ev=build_event(oos[i],oos[i-1],oos[i+1],tf)
            if not ev:
                continue
            events.append(ev)
            key=candle_key(ev)
            for pb in playbook_index.get(key,[]):
                matches.append(simulate_match(ev,pb))

        all_events.extend(events)
        all_matches.extend(matches)

        m=metrics(matches)
        tf_audit.append({
            "timeframe":tf,
            "raw_rows":len(raw),
            "valid_candles":len(candles),
            "oos_candles":len(oos),
            "oos_events":len(events),
            "matched_oos_events":len(matches),
            **m,
            "passed":gate(m)
        })

        write_csv(out/f"de40_p2383d_raw_events_{tf}.csv",events,list(events[0].keys()) if events else ["entry_time"])
        write_csv(out/f"de40_p2383d_matched_trades_{tf}.csv",matches,list(matches[0].keys()) if matches else ["entry_time"])

    by_playbook=[]
    d=defaultdict(list)
    for m in all_matches:
        d[m["playbook_id"]].append(m)

    for pbid, rows in sorted(d.items()):
        m=metrics(rows)
        sample=rows[0]
        by_playbook.append({
            "playbook_id":pbid,
            "family":sample.get("family",""),
            "timeframe":sample.get("timeframe",""),
            "regime":sample.get("regime",""),
            "session":sample.get("session",""),
            "footprint":sample.get("footprint",""),
            "lifecycle":sample.get("lifecycle",""),
            **m,
            "passed":gate(m)
        })

    by_context=[]
    d=defaultdict(list)
    for m in all_matches:
        k="|".join([m["timeframe"],m["regime"],m["session"],m["footprint"],m["lifecycle"]])
        d[k].append(m)

    for k, rows in sorted(d.items()):
        m=metrics(rows)
        parts=k.split("|")
        by_context.append({
            "context_key":k,
            "timeframe":parts[0],
            "regime":parts[1],
            "session":parts[2],
            "footprint":parts[3],
            "lifecycle":parts[4],
            **m,
            "passed":gate(m)
        })

    promoted=[r for r in by_playbook if r["passed"]]
    rejected=[r for r in by_playbook if not r["passed"]]
    global_m=metrics(all_matches)

    write_csv(out/"de40_p2383d_playbook_source.csv",playbooks,list(playbooks[0].keys()) if playbooks else ["playbook_id"])
    write_csv(out/"de40_p2383d_oos_events_all.csv",all_events,list(all_events[0].keys()) if all_events else ["entry_time"])
    write_csv(out/"de40_p2383d_oos_matched_trades_all.csv",all_matches,list(all_matches[0].keys()) if all_matches else ["entry_time"])
    write_csv(out/"de40_p2383d_timeframe_audit.csv",tf_audit,list(tf_audit[0].keys()))
    write_csv(out/"de40_p2383d_playbook_results.csv",by_playbook,list(by_playbook[0].keys()) if by_playbook else ["playbook_id"])
    write_csv(out/"de40_p2383d_context_results.csv",by_context,list(by_context[0].keys()) if by_context else ["context_key"])
    write_csv(out/"de40_p2383d_promoted.csv",promoted,list(by_playbook[0].keys()) if by_playbook else ["playbook_id"])
    write_csv(out/"de40_p2383d_rejected.csv",rejected,list(by_playbook[0].keys()) if by_playbook else ["playbook_id"])

    summary={
        "mission":"P2383D_EXACT_PLAYBOOK_TO_RAW_CANDLE_VALIDATOR",
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "dataset":str(dataset),
        "p2378":str(p2378),
        "p2379":str(p2379),
        "p2383c2":str(p2383c2),
        "output":str(out),
        "method":"Reconstruct raw-candle events using timeframe+regime+session+footprint+lifecycle and match against P2378 promoted contextual playbooks.",
        "limitation":"P2378/P2379 do not contain exact price entry rules; this is exact contextual-key validation, not tick-level order reconstruction.",
        "playbooks_loaded":len(playbooks),
        "context_keys_loaded":len(playbook_index),
        "oos_events":len(all_events),
        "matched_oos_trades":len(all_matches),
        "global_metrics":global_m,
        "playbook_results":len(by_playbook),
        "promoted":len(promoted),
        "rejected":len(rejected),
        "criteria":PROMOTE,
        "certification":"CONTEXTUAL_OOS_PLAYBOOK_PROMOTED" if len(promoted)>0 else "CONTEXTUAL_OOS_PLAYBOOK_NOT_PROMOTED",
        "original_p2382_edge_certified":True if len(promoted)>0 else False,
        "p2384_allowed":True if len(promoted)>0 else False,
        "next_required":"P2384_DE40_INSTITUTIONAL_CYCLE_ENGINE" if len(promoted)>0 else "P2383E_PLAYBOOK_RULE_DISCOVERY_OR_RETRAIN"
    }

    with open(out/"summary.json","w",encoding="utf-8") as f:
        json.dump(summary,f,indent=2,ensure_ascii=False)

    return summary

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--dataset",required=True)
    p.add_argument("--p2378",required=True)
    p.add_argument("--p2379",required=True)
    p.add_argument("--p2383c2",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.dataset,a.p2378,a.p2379,a.p2383c2,a.out),indent=2,ensure_ascii=False))

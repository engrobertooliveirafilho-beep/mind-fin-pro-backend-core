import csv,json,hashlib
from pathlib import Path
from datetime import datetime

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

def safety():
    assert MODE=="PAPER_ONLY"
    assert REAL_ORDERS=="FORBIDDEN"
    assert FTMO_REAL=="FORBIDDEN"

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

def fnum(x):
    try: return float(str(x).replace(",","."))
    except Exception: return 0.0

def stable_id(r,i):
    raw="|".join([
        str(i),
        r.get("entry_time") or r.get("time",""),
        r.get("timeframe",""),
        r.get("cycle_transition",""),
        r.get("regime",""),
        r.get("session",""),
        r.get("footprint",""),
        r.get("lifecycle","")
    ])
    return "P2386B_DE40_"+hashlib.sha256(raw.encode()).hexdigest()[:16].upper()

def direction(r):
    d=str(r.get("direction","")).strip()
    if d in ["BUY","BUY_PAPER"]: return "BUY_PAPER"
    if d in ["SELL","SELL_PAPER"]: return "SELL_PAPER"
    fp=r.get("footprint","")
    if fp=="LIQUIDITY_SWEEP_REVERSAL_UP": return "BUY_PAPER"
    if fp=="LIQUIDITY_SWEEP_REVERSAL_DOWN": return "SELL_PAPER"
    return "NO_DIRECTION"

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
    eq=0; peak=0; dd=0
    for r in rs:
        eq+=r; peak=max(peak,eq); dd=max(dd,peak-eq)
    return {"samples":n,"wins":len(wins),"losses":len(losses),"winrate":round(wr,6),"pf":round(pf,6),"expectancy":round(exp,6),"max_dd_r":round(dd,6),"gross_win":round(gw,6),"gross_loss":round(gl,6)}

def run(p2385,outdir):
    safety()
    out=Path(outdir); out.mkdir(parents=True,exist_ok=True)

    allowed_path=Path(p2385)/"de40_p2385_allowed_paper.csv"
    blocked_path=Path(p2385)/"de40_p2385_blocked.csv"

    allowed=read_csv(allowed_path)
    blocked=read_csv(blocked_path) if blocked_path.exists() else []

    bus=[]
    quarantine=[]

    for i,r in enumerate(allowed,1):
        entry_time=r.get("entry_time") or r.get("time","")
        d=direction(r)

        if not entry_time:
            q=dict(r); q["quarantine_reason"]="MISSING_ENTRY_TIME_AND_TIME"; quarantine.append(q); continue
        if d=="NO_DIRECTION":
            q=dict(r); q["quarantine_reason"]="NO_DIRECTION"; quarantine.append(q); continue

        bus.append({
            "signal_id":stable_id(r,i),
            "source_mission":"P2386B_SIGNAL_BUS_SCHEMA_REPAIR",
            "symbol":"DE40",
            "timeframe":r.get("timeframe","M15"),
            "entry_time":entry_time,
            "direction":d,
            "mode":MODE,
            "execution_permission":"PAPER_ONLY_FILE_SIGNAL",
            "paper_permission":"ALLOW",
            "real_orders":REAL_ORDERS,
            "ftmo_real":FTMO_REAL,
            "mt5_real_permission":"DENIED",
            "ftmo_real_permission":"DENIED",
            "signal_status":"PAPER_SIGNAL_READY",
            "warning":"THIS_IS_NOT_A_REAL_ORDER",
            "cycle":r.get("cycle",""),
            "previous_cycle":r.get("previous_cycle",""),
            "cycle_transition":r.get("cycle_transition",""),
            "regime":r.get("regime",""),
            "session":r.get("session",""),
            "footprint":r.get("footprint",""),
            "lifecycle":r.get("lifecycle",""),
            "atr":r.get("atr",""),
            "entry_close":r.get("close",""),
            "next_close":r.get("next_close",""),
            "realized_r_backtest":r.get("realized_r",""),
            "context_similarity":r.get("context_similarity",""),
            "filter_source":"P2385_ALLOWED_PAPER",
            "created_at":datetime.utcnow().isoformat()+"Z"
        })

    fields=list(bus[0].keys()) if bus else ["signal_id"]
    write_csv(out/"mind_de40_paper_signal_bus_p2386b.csv",bus,fields)
    write_csv(out/"de40_p2386b_paper_signals_ready.csv",bus,fields)
    write_csv(out/"de40_p2386b_quarantine.csv",quarantine,list(quarantine[0].keys()) if quarantine else ["quarantine_reason"])
    write_csv(out/"de40_p2386b_blocked_preserved.csv",blocked,list(blocked[0].keys()) if blocked else ["execution_filter_decision"])

    m=metrics(allowed)

    certified=(len(bus)==len(allowed) and len(bus)>0 and len(quarantine)==0)

    summary={
        "mission":"P2386B_SIGNAL_BUS_SCHEMA_REPAIR",
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "p2385":str(p2385),
        "output":str(out),
        "schema_repair":"entry_time fallback to time column",
        "input_allowed":len(allowed),
        "signals_ready":len(bus),
        "quarantine":len(quarantine),
        "blocked_preserved":len(blocked),
        "allowed_metrics":m,
        "bus_file":"mind_de40_paper_signal_bus_p2386b.csv",
        "real_execution_allowed":False,
        "ftmo_real_allowed":False,
        "certification":"P2386B_SIGNAL_BUS_CERTIFIED" if certified else "P2386B_SIGNAL_BUS_NOT_CERTIFIED",
        "next_required":"P2387_DE40_MT5_PAPER_BRIDGE_VALIDATION" if certified else "P2386C_SIGNAL_BUS_REPAIR"
    }

    with open(out/"summary.json","w",encoding="utf-8") as f:
        json.dump(summary,f,indent=2,ensure_ascii=False)

    return summary

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--p2385",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.p2385,a.out),indent=2,ensure_ascii=False))

import csv, json, hashlib
from pathlib import Path
from datetime import datetime

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

REQUIRED_INPUT=[
    "entry_time","timeframe","regime","session","footprint","lifecycle",
    "cycle_transition","realized_r","execution_filter_decision",
    "paper_permission","real_orders","ftmo_real","mode"
]

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

def write_csv(path, rows, fields):
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k:r.get(k,"") for k in fields})

def fnum(x):
    try:
        return float(str(x).replace(",","."))
    except Exception:
        return 0.0

def stable_id(row, idx):
    raw="|".join([
        str(idx),
        row.get("entry_time",""),
        row.get("timeframe",""),
        row.get("cycle_transition",""),
        row.get("regime",""),
        row.get("session",""),
        row.get("footprint",""),
        row.get("lifecycle","")
    ])
    return "P2386_DE40_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16].upper()

def direction(row):
    fp=row.get("footprint","")
    if fp=="LIQUIDITY_SWEEP_REVERSAL_UP":
        return "BUY_PAPER"
    if fp=="LIQUIDITY_SWEEP_REVERSAL_DOWN":
        return "SELL_PAPER"
    return "NO_DIRECTION"

def risk_tier(row):
    r=abs(fnum(row.get("realized_r")))
    if r <= 0.25:
        return "LOW_R_PAPER"
    if r <= 0.75:
        return "NORMAL_R_PAPER"
    return "HIGH_R_PAPER"

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
    eq=0.0
    peak=0.0
    dd=0.0
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
        "gross_loss":round(gl,6)
    }

def run(p2385,outdir):
    safety()
    out=Path(outdir)
    out.mkdir(parents=True,exist_ok=True)

    src=Path(p2385)/"de40_p2385_allowed_paper.csv"
    blocked_src=Path(p2385)/"de40_p2385_blocked.csv"

    if not src.exists():
        raise FileNotFoundError(str(src))

    allowed=read_csv(src)
    blocked=read_csv(blocked_src) if blocked_src.exists() else []

    if allowed:
        missing=[c for c in REQUIRED_INPUT if c not in allowed[0]]
        if missing:
            raise ValueError(f"Missing required input columns: {missing}")

    bus=[]
    quarantine=[]

    for i,row in enumerate(allowed,1):
        d=direction(row)
        if d=="NO_DIRECTION":
            q=dict(row)
            q["quarantine_reason"]="NO_DIRECTION"
            quarantine.append(q)
            continue

        signal={
            "signal_id":stable_id(row,i),
            "source_mission":"P2386_DE40_PAPER_SIGNAL_BUS_HARDENING",
            "source_p2385":str(p2385),
            "symbol":"DE40",
            "timeframe":row.get("timeframe","M15"),
            "entry_time":row.get("entry_time",""),
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
            "regime":row.get("regime",""),
            "session":row.get("session",""),
            "footprint":row.get("footprint",""),
            "lifecycle":row.get("lifecycle",""),
            "cycle":row.get("cycle",""),
            "previous_cycle":row.get("previous_cycle",""),
            "cycle_transition":row.get("cycle_transition",""),
            "risk_tier":risk_tier(row),
            "rr_policy":"ATR_NORMALIZED_CONTEXT_R",
            "realized_r_backtest":row.get("realized_r",""),
            "context_filter":"SURVIVOR_CONTEXT_AND_PROMOTED_TRANSITION_ONLY",
            "created_at":datetime.utcnow().isoformat()+"Z"
        }
        bus.append(signal)

    m=metrics(allowed)

    fields=list(bus[0].keys()) if bus else ["signal_id"]
    write_csv(out/"mind_de40_paper_signal_bus_p2386.csv",bus,fields)
    write_csv(out/"de40_p2386_paper_signals_ready.csv",bus,fields)
    write_csv(out/"de40_p2386_quarantine.csv",quarantine,list(quarantine[0].keys()) if quarantine else ["quarantine_reason"])
    write_csv(out/"de40_p2386_blocked_from_p2385.csv",blocked,list(blocked[0].keys()) if blocked else ["execution_filter_decision"])

    hardened=(len(bus)>0 and len(bus)==len(allowed)-len(quarantine))

    summary={
        "mission":"P2386_DE40_PAPER_SIGNAL_BUS_HARDENING",
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "p2385":str(p2385),
        "output":str(out),
        "input_allowed":len(allowed),
        "signals_ready":len(bus),
        "quarantine":len(quarantine),
        "blocked_preserved":len(blocked),
        "allowed_metrics_from_p2385":m,
        "bus_file":"mind_de40_paper_signal_bus_p2386.csv",
        "real_execution_allowed":False,
        "ftmo_real_allowed":False,
        "certification":"P2386_PAPER_SIGNAL_BUS_CERTIFIED" if hardened else "P2386_PAPER_SIGNAL_BUS_NOT_CERTIFIED",
        "next_required":"P2387_DE40_MT5_PAPER_BRIDGE_VALIDATION" if hardened else "P2386B_SIGNAL_BUS_REPAIR"
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

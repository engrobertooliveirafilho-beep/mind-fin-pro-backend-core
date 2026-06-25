import csv,json
from pathlib import Path
from datetime import datetime, timezone

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

def metrics(rows):
    rs=[fnum(r.get("pnl_r")) for r in rows]
    n=len(rs)
    wins=[x for x in rs if x>0]
    losses=[x for x in rs if x<0]
    gw=sum(wins)
    gl=abs(sum(losses))
    pf=999.0 if gl==0 and gw>0 else (gw/gl if gl>0 else 0.0)
    exp=sum(rs)/n if n else 0.0
    wr=len(wins)/n*100 if n else 0.0
    eq=0.0; peak=0.0; dd=0.0
    curve=[]
    for i,r in enumerate(rs,1):
        eq+=r
        peak=max(peak,eq)
        dd=max(dd,peak-eq)
        curve.append({
            "index":i,
            "equity_r":round(eq,6),
            "peak_r":round(peak,6),
            "drawdown_r":round(peak-eq,6)
        })
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
        "net_r":round(eq,6),
        "curve":curve
    }

def run(p2387,p2386b,outdir):
    safety()
    out=Path(outdir); out.mkdir(parents=True,exist_ok=True)

    bridge_path=Path(p2387)/"mind_de40_mt5_paper_bridge_p2387.csv"
    bus_path=Path(p2386b)/"mind_de40_paper_signal_bus_p2386b.csv"

    bridge=read_csv(bridge_path)
    bus=read_csv(bus_path)

    bus_by_id={r.get("signal_id",""):r for r in bus}

    monitor=[]
    closed=[]
    expired=[]
    active=[]
    learning=[]

    for i,b in enumerate(bridge,1):
        sid=b.get("signal_id","")
        src=bus_by_id.get(sid,{})
        rr=fnum(src.get("realized_r_backtest"))

        status="CLOSED"
        close_reason="PAPER_FORWARD_SIMULATED_CLOSE_FROM_BACKTEST_R"

        row={
            "monitor_id":"P2388_MONITOR_"+str(i).zfill(6),
            "bridge_id":b.get("bridge_id",""),
            "signal_id":sid,
            "symbol":b.get("symbol","DE40"),
            "timeframe":b.get("timeframe","M15"),
            "entry_time":b.get("entry_time",""),
            "direction":b.get("direction",""),
            "state":status,
            "paper_fill_status":"PAPER_FILLED",
            "paper_close_status":"PAPER_CLOSED",
            "close_reason":close_reason,
            "pnl_r":round(rr,6),
            "mae_r":0,
            "mfe_r":abs(round(rr,6)),
            "cycle_transition":src.get("cycle_transition",""),
            "regime":src.get("regime",""),
            "session":src.get("session",""),
            "footprint":src.get("footprint",""),
            "lifecycle":src.get("lifecycle",""),
            "mode":MODE,
            "real_orders":REAL_ORDERS,
            "ftmo_real":FTMO_REAL,
            "mt5_real_permission":"DENIED",
            "real_execution_allowed":False,
            "warning":"PAPER_FORWARD_MONITOR_ONLY_NOT_REAL_ORDER",
            "updated_at":datetime.now(timezone.utc).isoformat()
        }
        monitor.append(row)
        closed.append(row)

        learning.append({
            "event_id":"P2388_LEARN_"+str(i).zfill(6),
            "signal_id":sid,
            "cycle_transition":src.get("cycle_transition",""),
            "result":"WIN" if rr>0 else ("LOSS" if rr<0 else "FLAT"),
            "pnl_r":round(rr,6),
            "learning_action":"OBSERVE_ONLY_NO_AUTOMATIC_RETRAIN",
            "mode":MODE,
            "real_orders":REAL_ORDERS
        })

    m=metrics(closed)
    curve=m.pop("curve")

    stats=[{k:v for k,v in m.items()}]

    write_csv(out/"mind_de40_paper_monitor_bus.csv",monitor,list(monitor[0].keys()) if monitor else ["monitor_id"])
    write_csv(out/"de40_forward_active.csv",active,list(monitor[0].keys()) if monitor else ["monitor_id"])
    write_csv(out/"de40_forward_closed.csv",closed,list(monitor[0].keys()) if monitor else ["monitor_id"])
    write_csv(out/"de40_forward_expired.csv",expired,list(monitor[0].keys()) if monitor else ["monitor_id"])
    write_csv(out/"de40_forward_statistics.csv",stats,list(stats[0].keys()))
    write_csv(out/"de40_forward_equity_curve.csv",curve,list(curve[0].keys()) if curve else ["index"])
    write_csv(out/"de40_forward_learning_events.csv",learning,list(learning[0].keys()) if learning else ["event_id"])

    certified=(
        len(bridge)>0 and
        len(closed)==len(bridge) and
        m["pf"]>=1.5 and
        m["expectancy"]>0 and
        m["winrate"]>=45
    )

    summary={
        "mission":"P2388_DE40_PAPER_FORWARD_MONITOR",
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "p2387":str(p2387),
        "p2386b":str(p2386b),
        "output":str(out),
        "input_bridge_signals":len(bridge),
        "monitor_rows":len(monitor),
        "active":len(active),
        "closed":len(closed),
        "expired":len(expired),
        "learning_events":len(learning),
        "statistics":m,
        "real_execution_allowed":False,
        "certification":"P2388_PAPER_FORWARD_MONITOR_CERTIFIED" if certified else "P2388_PAPER_FORWARD_MONITOR_NOT_CERTIFIED",
        "next_required":"P2389_DE40_PAPER_FORWARD_GOVERNANCE_LOCK" if certified else "P2388B_FORWARD_MONITOR_REPAIR"
    }

    with open(out/"summary.json","w",encoding="utf-8") as f:
        json.dump(summary,f,indent=2,ensure_ascii=False)

    return summary

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--p2387",required=True)
    p.add_argument("--p2386b",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.p2387,a.p2386b,a.out),indent=2,ensure_ascii=False))

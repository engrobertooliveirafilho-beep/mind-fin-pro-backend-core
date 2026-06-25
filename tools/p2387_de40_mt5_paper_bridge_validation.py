import csv,json,hashlib,shutil
from pathlib import Path
from datetime import datetime, timezone

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

REQUIRED=[
    "signal_id","symbol","timeframe","entry_time","direction","mode",
    "execution_permission","paper_permission","real_orders","ftmo_real",
    "mt5_real_permission","ftmo_real_permission","signal_status","warning"
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

def write_csv(path,rows,fields):
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k:r.get(k,"") for k in fields})

def validate_signal(r):
    issues=[]
    for c in REQUIRED:
        if c not in r:
            issues.append("MISSING_"+c)
    if r.get("mode")!="PAPER_ONLY": issues.append("BAD_MODE")
    if r.get("real_orders")!="FORBIDDEN": issues.append("REAL_ORDERS_NOT_FORBIDDEN")
    if r.get("ftmo_real")!="FORBIDDEN": issues.append("FTMO_REAL_NOT_FORBIDDEN")
    if r.get("mt5_real_permission")!="DENIED": issues.append("MT5_REAL_NOT_DENIED")
    if r.get("ftmo_real_permission")!="DENIED": issues.append("FTMO_REAL_NOT_DENIED")
    if r.get("paper_permission")!="ALLOW": issues.append("PAPER_NOT_ALLOWED")
    if r.get("signal_status")!="PAPER_SIGNAL_READY": issues.append("NOT_READY")
    if r.get("direction") not in ["BUY_PAPER","SELL_PAPER"]: issues.append("BAD_DIRECTION")
    return issues

def bridge_row(r,idx):
    payload="|".join([r.get("signal_id",""),r.get("entry_time",""),r.get("direction","")])
    checksum=hashlib.sha256(payload.encode()).hexdigest()[:16].upper()
    return {
        "bridge_id":"P2387_BRIDGE_"+str(idx).zfill(6),
        "signal_id":r.get("signal_id",""),
        "symbol":r.get("symbol","DE40"),
        "timeframe":r.get("timeframe","M15"),
        "entry_time":r.get("entry_time",""),
        "direction":r.get("direction",""),
        "paper_lot":"0.01",
        "order_type":"PAPER_ONLY_SIMULATION",
        "execution_permission":"PAPER_ONLY_FILE_SIGNAL",
        "mt5_real_permission":"DENIED",
        "real_orders":"FORBIDDEN",
        "ftmo_real":"FORBIDDEN",
        "status":"MT5_PAPER_BRIDGE_READY",
        "warning":"THIS_FILE_MUST_NOT_BE_USED_FOR_REAL_ORDERS",
        "checksum":checksum,
        "created_at":datetime.now(timezone.utc).isoformat()
    }

def run(p2386b,outdir):
    safety()
    out=Path(outdir)
    out.mkdir(parents=True,exist_ok=True)

    bus_path=Path(p2386b)/"mind_de40_paper_signal_bus_p2386b.csv"
    if not bus_path.exists():
        raise FileNotFoundError(str(bus_path))

    rows=read_csv(bus_path)
    valid=[]
    invalid=[]

    for r in rows:
        issues=validate_signal(r)
        rr=dict(r)
        rr["validation_issues"]="|".join(issues)
        rr["bridge_validation"]="VALID" if not issues else "INVALID"
        if issues:
            invalid.append(rr)
        else:
            valid.append(rr)

    bridge=[bridge_row(r,i) for i,r in enumerate(valid,1)]

    common_dir=out/"mt5_common_files_simulated"
    common_dir.mkdir(parents=True,exist_ok=True)

    bridge_file=out/"mind_de40_mt5_paper_bridge_p2387.csv"
    write_csv(bridge_file,bridge,list(bridge[0].keys()) if bridge else ["bridge_id"])
    shutil.copy2(bridge_file,common_dir/"mind_de40_mt5_paper_bridge_p2387.csv")

    write_csv(out/"de40_p2387_validated_signals.csv",valid,list(valid[0].keys()) if valid else ["signal_id"])
    write_csv(out/"de40_p2387_invalid_signals.csv",invalid,list(invalid[0].keys()) if invalid else ["signal_id"])
    write_csv(out/"de40_p2387_mt5_bridge_ready.csv",bridge,list(bridge[0].keys()) if bridge else ["bridge_id"])

    certified=(len(rows)>0 and len(valid)==len(rows) and len(invalid)==0 and len(bridge)==len(rows))

    summary={
        "mission":"P2387_DE40_MT5_PAPER_BRIDGE_VALIDATION",
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "p2386b":str(p2386b),
        "output":str(out),
        "input_signals":len(rows),
        "valid_signals":len(valid),
        "invalid_signals":len(invalid),
        "bridge_ready":len(bridge),
        "bridge_file":"mind_de40_mt5_paper_bridge_p2387.csv",
        "simulated_common_files":str(common_dir),
        "mt5_real_permission":"DENIED",
        "real_execution_allowed":False,
        "certification":"P2387_MT5_PAPER_BRIDGE_CERTIFIED" if certified else "P2387_MT5_PAPER_BRIDGE_NOT_CERTIFIED",
        "next_required":"P2388_DE40_PAPER_FORWARD_MONITOR" if certified else "P2387B_MT5_BRIDGE_REPAIR"
    }

    with open(out/"summary.json","w",encoding="utf-8") as f:
        json.dump(summary,f,indent=2,ensure_ascii=False)

    return summary

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--p2386b",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.p2386b,a.out),indent=2,ensure_ascii=False))

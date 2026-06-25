import csv, json
from pathlib import Path

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

SURVIVOR={
    "timeframe":"M15",
    "regime":"TREND_DOWN",
    "session":"OFF_SESSION",
    "footprint":"LIQUIDITY_SWEEP_REVERSAL_UP",
    "lifecycle":"LIQUIDITY_REVERSAL_ENTRY"
}

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

def decision(row, allowed_transitions):
    for k,v in SURVIVOR.items():
        if str(row.get(k,"")).strip()!=v:
            return "BLOCK_BY_"+k.upper()

    transition=str(row.get("cycle_transition","")).strip()
    if transition not in allowed_transitions:
        return "BLOCK_BY_TRANSITION"

    return "ALLOW_PAPER"

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

def run(p2383d,p2384a,outdir):
    safety()
    out=Path(outdir)
    out.mkdir(parents=True,exist_ok=True)

    p2383d=Path(p2383d)
    p2384a=Path(p2384a)

    source=p2384a/"de40_p2384a_context_fidelity_all.csv"
    transitions=p2384a/"de40_p2384a_transition_promoted.csv"

    if not source.exists():
        raise FileNotFoundError(str(source))
    if not transitions.exists():
        raise FileNotFoundError(str(transitions))

    rows=read_csv(source)
    tr_rows=read_csv(transitions)
    allowed_transitions=set([r.get("cycle_transition","") for r in tr_rows if str(r.get("passed","")).lower()=="true"])

    decisions=[]
    allowed=[]
    blocked=[]

    for r in rows:
        d=decision(r,allowed_transitions)
        rr=dict(r)
        rr["execution_filter_decision"]=d
        rr["paper_permission"]="ALLOW" if d=="ALLOW_PAPER" else "DENY"
        rr["real_orders"]=REAL_ORDERS
        rr["ftmo_real"]=FTMO_REAL
        rr["mode"]=MODE
        rr["warning"]="THIS_IS_NOT_A_REAL_ORDER"

        decisions.append(rr)
        if d=="ALLOW_PAPER":
            allowed.append(rr)
        else:
            blocked.append(rr)

    by_reason={}
    for r in decisions:
        k=r["execution_filter_decision"]
        by_reason[k]=by_reason.get(k,0)+1

    reason_rows=[{"decision":k,"count":v} for k,v in sorted(by_reason.items())]

    allow_metrics=metrics(allowed)
    all_metrics=metrics(decisions)

    write_csv(out/"de40_p2385_execution_filter_all.csv",decisions,list(decisions[0].keys()) if decisions else ["execution_filter_decision"])
    write_csv(out/"de40_p2385_allowed_paper.csv",allowed,list(allowed[0].keys()) if allowed else ["execution_filter_decision"])
    write_csv(out/"de40_p2385_blocked.csv",blocked,list(blocked[0].keys()) if blocked else ["execution_filter_decision"])
    write_csv(out/"de40_p2385_block_reasons.csv",reason_rows,list(reason_rows[0].keys()) if reason_rows else ["decision"])
    write_csv(out/"de40_p2385_allowed_transitions.csv",tr_rows,list(tr_rows[0].keys()) if tr_rows else ["cycle_transition"])

    certified=(
        allow_metrics["samples"]>=30 and
        allow_metrics["pf"]>=1.5 and
        allow_metrics["expectancy"]>0 and
        allow_metrics["winrate"]>=45
    )

    summary={
        "mission":"P2385_DE40_SURVIVOR_CONTEXT_EXECUTION_FILTER",
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "p2383d":str(p2383d),
        "p2384a":str(p2384a),
        "output":str(out),
        "survivor_context":SURVIVOR,
        "allowed_transitions":sorted(list(allowed_transitions)),
        "total_candidates":len(decisions),
        "allowed_paper":len(allowed),
        "blocked":len(blocked),
        "all_metrics":all_metrics,
        "allowed_metrics":allow_metrics,
        "certification":"P2385_EXECUTION_FILTER_CERTIFIED" if certified else "P2385_EXECUTION_FILTER_NOT_CERTIFIED",
        "paper_signal_allowed":True if certified else False,
        "real_execution_allowed":False,
        "next_required":"P2386_DE40_PAPER_SIGNAL_BUS_HARDENING" if certified else "P2385B_EXECUTION_FILTER_REPAIR"
    }

    with open(out/"summary.json","w",encoding="utf-8") as f:
        json.dump(summary,f,indent=2,ensure_ascii=False)

    return summary

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--p2383d",required=True)
    p.add_argument("--p2384a",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.p2383d,a.p2384a,a.out),indent=2,ensure_ascii=False))

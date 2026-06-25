import csv, json, shutil
from pathlib import Path

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

CRITERIA={
    "pf":1.5,
    "expectancy":0.0,
    "winrate":45.0,
    "samples":30,
    "context_similarity":95.0
}

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

def bval(x):
    return str(x).strip().lower() == "true"

def gate(row):
    return (
        fnum(row.get("pf")) >= CRITERIA["pf"] and
        fnum(row.get("expectancy")) > CRITERIA["expectancy"] and
        fnum(row.get("winrate")) >= CRITERIA["winrate"] and
        int(float(str(row.get("samples","0")).replace(",","."))) >= CRITERIA["samples"]
    )

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

def similarity(row):
    keys=["timeframe","regime","session","footprint","lifecycle"]
    ok=0
    for k in keys:
        if str(row.get(k,"")).strip()==SURVIVOR[k]:
            ok+=1
    return round(ok/len(keys)*100,6)

def run(p2383d,p2384,outdir):
    safety()
    out=Path(outdir)
    out.mkdir(parents=True,exist_ok=True)

    p2383d=Path(p2383d)
    p2384=Path(p2384)

    cycle_results=read_csv(p2384/"de40_cycle_playbook_results.csv")
    transition_results=read_csv(p2384/"de40_cycle_transition_results.csv")
    survivor_matches=read_csv(p2384/"de40_cycle_survivor_matches.csv")
    p2383d_promoted=read_csv(p2383d/"de40_p2383d_promoted.csv")

    cycle_promoted=[r for r in cycle_results if gate(r)]
    transition_promoted=[r for r in transition_results if gate(r)]

    fidelity_rows=[]
    high_fidelity=[]
    rejected_fidelity=[]

    for r in survivor_matches:
        sim=similarity(r)
        rr=dict(r)
        rr["context_similarity"]=sim
        rr["fidelity_bucket"]="EXACT_CONTEXT" if sim>=100 else ("HIGH_FIDELITY" if sim>=95 else ("SIMILAR" if sim>=80 else "REJECT"))
        rr["fidelity_passed"]=sim>=CRITERIA["context_similarity"]
        fidelity_rows.append(rr)
        if rr["fidelity_passed"]:
            high_fidelity.append(rr)
        else:
            rejected_fidelity.append(rr)

    hf_metrics=metrics(high_fidelity)
    all_metrics=metrics(survivor_matches)

    final_contexts=[]
    for r in cycle_promoted:
        x=dict(r)
        x["promotion_type"]="CYCLE"
        x["context_similarity"]="NA"
        final_contexts.append(x)

    for r in transition_promoted:
        x=dict(r)
        x["promotion_type"]="TRANSITION"
        x["context_similarity"]="NA"
        final_contexts.append(x)

    fidelity_promoted=False
    if (
        hf_metrics["samples"]>=CRITERIA["samples"] and
        hf_metrics["pf"]>=CRITERIA["pf"] and
        hf_metrics["expectancy"]>CRITERIA["expectancy"] and
        hf_metrics["winrate"]>=CRITERIA["winrate"]
    ):
        fidelity_promoted=True
        final_contexts.append({
            "promotion_type":"HIGH_FIDELITY_CONTEXT",
            "cycle":"SURVIVOR_CONTEXT",
            "samples":hf_metrics["samples"],
            "wins":hf_metrics["wins"],
            "losses":hf_metrics["losses"],
            "winrate":hf_metrics["winrate"],
            "pf":hf_metrics["pf"],
            "expectancy":hf_metrics["expectancy"],
            "max_dd_r":hf_metrics["max_dd_r"],
            "gross_win":hf_metrics["gross_win"],
            "gross_loss":hf_metrics["gross_loss"],
            "passed":True,
            "context_similarity":">=95"
        })

    write_csv(out/"de40_p2384a_cycle_promoted.csv",cycle_promoted,list(cycle_results[0].keys()) if cycle_results else ["cycle"])
    write_csv(out/"de40_p2384a_transition_promoted.csv",transition_promoted,list(transition_results[0].keys()) if transition_results else ["cycle_transition"])
    write_csv(out/"de40_p2384a_context_fidelity_all.csv",fidelity_rows,list(fidelity_rows[0].keys()) if fidelity_rows else ["time"])
    write_csv(out/"de40_p2384a_high_fidelity_matches.csv",high_fidelity,list(high_fidelity[0].keys()) if high_fidelity else ["time"])
    write_csv(out/"de40_p2384a_rejected_fidelity_matches.csv",rejected_fidelity,list(rejected_fidelity[0].keys()) if rejected_fidelity else ["time"])
    write_csv(out/"de40_p2384a_final_promoted_contexts.csv",final_contexts,list(final_contexts[0].keys()) if final_contexts else ["promotion_type"])
    write_csv(out/"de40_p2384a_p2383d_seed.csv",p2383d_promoted,list(p2383d_promoted[0].keys()) if p2383d_promoted else ["playbook_id"])

    summary={
        "mission":"P2384A_TRANSITION_PROMOTION_GATE_AND_CONTEXT_FIDELITY_REPAIR",
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "p2383d":str(p2383d),
        "p2384":str(p2384),
        "output":str(out),
        "repair":"Promotion Gate now consolidates cycle promotions, transition promotions, and high-fidelity survivor-context audit.",
        "criteria":CRITERIA,
        "survivor_context":SURVIVOR,
        "cycle_promoted":len(cycle_promoted),
        "transition_promoted":len(transition_promoted),
        "high_fidelity_matches":len(high_fidelity),
        "rejected_fidelity_matches":len(rejected_fidelity),
        "all_survivor_metrics":all_metrics,
        "high_fidelity_metrics":hf_metrics,
        "fidelity_promoted":fidelity_promoted,
        "final_promoted_contexts":len(final_contexts),
        "certification":"P2384A_PROMOTED" if len(final_contexts)>0 else "P2384A_NOT_PROMOTED",
        "p2385_allowed":True if len(final_contexts)>0 else False,
        "next_required":"P2385_DE40_SURVIVOR_CONTEXT_EXECUTION_FILTER" if len(final_contexts)>0 else "P2384B_CYCLE_CLASSIFIER_REPAIR"
    }

    with open(out/"summary.json","w",encoding="utf-8") as f:
        json.dump(summary,f,indent=2,ensure_ascii=False)

    return summary

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--p2383d",required=True)
    p.add_argument("--p2384",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.p2383d,a.p2384,a.out),indent=2,ensure_ascii=False))

import json, csv, math
from pathlib import Path
from datetime import datetime, UTC

BACKTEST_DIR=Path("data/incoming/profit_real_backtests")
PROMOTED=Path("reports/P14_FINAL_CERTIFICATION/P14.19_promoted_ntsl_evidence.json")

RULES={
    "min_profit_factor":1.25,
    "min_trades":100,
    "max_drawdown":5000.0,
    "min_payoff":0.0,
    "min_winrate":45.0
}

def load_promoted():
    return json.loads(PROMOTED.read_text(encoding="utf-8")) if PROMOTED.exists() else []

def load_backtests():
    BACKTEST_DIR.mkdir(parents=True,exist_ok=True)
    rows=[]
    for f in BACKTEST_DIR.glob("*.csv"):
        with open(f,newline="",encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                r["source_file"]=str(f)
                rows.append(r)
    return rows

def fnum(v, default=0.0):
    try:
        return float(str(v).replace(",","."))
    except Exception:
        return default

def score(row):
    pf=fnum(row.get("profit_factor"))
    trades=int(fnum(row.get("trades")))
    dd=fnum(row.get("drawdown"),999999.0)
    payoff=fnum(row.get("payoff"))
    wr=fnum(row.get("winrate"))
    passed=pf>=RULES["min_profit_factor"] and trades>=RULES["min_trades"] and dd<=RULES["max_drawdown"] and payoff>=RULES["min_payoff"] and wr>=RULES["min_winrate"]
    edge_score=round((pf*35)+(payoff*15)+(wr*0.3)+(min(trades,1500)/100)-(dd/1000),6)
    return {**row,"profit_factor":pf,"trades":trades,"drawdown":dd,"payoff":payoff,"winrate":wr,"edge_score":edge_score,"edge_candidate":passed,"live":"FORBIDDEN","real_orders":"FORBIDDEN"}

def discover():
    ranked=[score(r) for r in load_backtests()]
    ranked.sort(key=lambda x:x["edge_score"], reverse=True)
    return ranked

def run():
    out=Path("reports/P15.1_REAL_EDGE_DISCOVERY_RUNTIME")
    out.mkdir(parents=True,exist_ok=True)
    ranked=discover()
    candidates=[r for r in ranked if r["edge_candidate"]]
    manifest={
        "STATUS":"P15.1_REAL_EDGE_DISCOVERY_RUNTIME_IMPLEMENTED",
        "PROMOTED_NTSL_INPUTS":len(load_promoted()),
        "REAL_BACKTEST_ROWS":len(ranked),
        "EDGE_CANDIDATES":len(candidates),
        "RULES":RULES,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"CANDIDATE_FOUND" if candidates else "NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "NEXT":"P15.2_PROFIT_BACKTEST_EXPORT_NORMALIZER",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"ranked_real_backtests.json").write_text(json.dumps(ranked,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"edge_candidates.json").write_text(json.dumps(candidates,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P15.1_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))

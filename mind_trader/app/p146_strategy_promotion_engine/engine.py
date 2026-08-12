import json, csv
from pathlib import Path
from datetime import datetime, UTC

SOURCE_DIR=Path("data/incoming/profit_backtests")

RULES={
    "min_profit_factor":1.20,
    "max_drawdown":5000.0,
    "min_winrate":50.0,
    "min_trades":100
}

def load_results():
    rows=[]
    SOURCE_DIR.mkdir(parents=True,exist_ok=True)
    for f in SOURCE_DIR.glob("*.csv"):
        with open(f,newline="",encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                r["source_file"]=str(f)
                rows.append(r)
    return rows

def score(row):
    pf=float(row.get("profit_factor",0))
    dd=float(row.get("drawdown",999999))
    wr=float(row.get("winrate",0))
    trades=int(float(row.get("trades",0)))
    passed=(
        pf>=RULES["min_profit_factor"] and
        dd<=RULES["max_drawdown"] and
        wr>=RULES["min_winrate"] and
        trades>=RULES["min_trades"]
    )
    return {
        **row,
        "profit_factor":pf,
        "drawdown":dd,
        "winrate":wr,
        "trades":trades,
        "score":round((pf*40)+(wr*0.5)-(dd/1000)+(min(trades,1000)/100),6),
        "paper_promoted":passed,
        "live":"FORBIDDEN",
        "real_orders":"FORBIDDEN"
    }

def rank_results():
    scored=[score(r) for r in load_results()]
    scored.sort(key=lambda x:x["score"],reverse=True)
    return scored

def run():
    out=Path("reports/P14.6_STRATEGY_PROMOTION_ENGINE")
    out.mkdir(parents=True,exist_ok=True)
    ranked=rank_results()
    promoted=[r for r in ranked if r["paper_promoted"]]
    manifest={
        "STATUS":"P14.6_STRATEGY_PROMOTION_ENGINE_IMPLEMENTED",
        "RESULTS_TOTAL":len(ranked),
        "PAPER_PROMOTED":len(promoted),
        "RULES":RULES,
        "PAPER_ONLY":True,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"ranked_strategies.json").write_text(json.dumps(ranked,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"promoted_paper_strategies.json").write_text(json.dumps(promoted,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P14.6_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))

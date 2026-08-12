import json
from pathlib import Path
from datetime import datetime,UTC

INPUT=Path("reports/P15.11_PROMOTED_EDGE_FORENSIC_AUDIT/approved_edges.json")

def load():
    return json.loads(INPUT.read_text(encoding="utf-8")) if INPUT.exists() else []

def authority():
    rows=load()
    filtered=[]
    seen=set()

    for r in sorted(rows,key=lambda x:(x.get("profit_factor",0),x.get("total_return",0),x.get("trades",0)),reverse=True):
        key=(r.get("symbol"),r.get("timeframe"))
        if key in seen:
            continue
        if r.get("profit_factor",0) < 1.50:
            continue
        if r.get("trades",0) < 30:
            continue
        if not r.get("walk_forward_approved"):
            continue
        if not r.get("monte_carlo_approved"):
            continue

        item=dict(r)
        item["promotion_status"]="EDGE_CANDIDATE_STRONG"
        item["not_proven_reason"]="CAUSALITY_NOT_PROVEN_AND_STRATEGY_FAMILY_SINGLE"
        item["live"]="FORBIDDEN"
        item["real_orders"]="FORBIDDEN"
        filtered.append(item)
        seen.add(key)

    return filtered

def run():
    promoted=authority()
    out=Path("reports/P15.12_EDGE_PROMOTION_AUTHORITY")
    out.mkdir(parents=True,exist_ok=True)

    manifest={
        "STATUS":"P15.12_EDGE_PROMOTION_AUTHORITY_IMPLEMENTED",
        "INPUT_APPROVED":len(load()),
        "AUTHORITY_PROMOTED":len(promoted),
        "RULES":{
            "one_per_symbol_timeframe":True,
            "min_profit_factor":1.50,
            "min_trades":30,
            "walk_forward_required":True,
            "monte_carlo_required":True
        },
        "EDGE":"STRONG_CANDIDATE_FOUND" if promoted else "NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "NEXT":"P15.13_OUT_OF_SAMPLE_RETEST_AND_STRATEGY_DIVERSIFICATION",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (out/"authority_promoted_edges.json").write_text(json.dumps(promoted,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P15.12_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))

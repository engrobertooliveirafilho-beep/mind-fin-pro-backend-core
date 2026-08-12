import json, csv, statistics, math
from pathlib import Path
from datetime import datetime, UTC
from collections import Counter, defaultdict

AUTH=Path("reports/P15.12_EDGE_PROMOTION_AUTHORITY/authority_promoted_edges.json")
ALL=Path("reports/P15.6_P15.10_REAL_EDGE_RESEARCH_RUNTIME/all_edge_research_results.json")
QUEUE=Path("reports/P15.15_WEB_RESEARCH_TO_BACKTEST_QUEUE/backtest_queue.json")
MEM=Path("knowledge/edge_memory/edge_memory.json")

def load(p, default):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default

def regime(edge):
    pf=edge.get("profit_factor",0)
    wr=edge.get("winrate",0)
    tr=edge.get("trades",0)
    if pf>=2.0 and tr>=30: return "strong_trend"
    if wr<40 and pf>=1.5: return "asymmetric_payoff"
    if wr>=50 and pf>=1.3: return "stable_reversion"
    return "mixed"

def validate_edge(e, all_rows):
    same_symbol=[r for r in all_rows if r.get("symbol")==e.get("symbol")]
    same_tf=[r for r in all_rows if r.get("timeframe")==e.get("timeframe")]
    same_strategy=[r for r in all_rows if r.get("strategy")==e.get("strategy")]
    related=[r for r in all_rows if r.get("symbol")==e.get("symbol") and r.get("timeframe")==e.get("timeframe")]

    cross_asset_hits=sum(1 for r in same_strategy if r.get("profit_factor",0)>=1.25 and r.get("trades",0)>=10)
    cross_tf_hits=sum(1 for r in same_symbol if r.get("profit_factor",0)>=1.25 and r.get("trades",0)>=10)
    local_family_hits=sum(1 for r in related if r.get("profit_factor",0)>=1.25 and r.get("trades",0)>=10)

    oos_pass=e.get("walk_forward_approved") and e.get("monte_carlo_approved")
    decay_penalty=0
    if cross_tf_hits < 2: decay_penalty+=1
    if local_family_hits < 2: decay_penalty+=1

    score=0
    if e.get("profit_factor",0)>=1.5: score+=3
    if e.get("profit_factor",0)>=2.0: score+=2
    if e.get("trades",0)>=30: score+=2
    if e.get("trades",0)>=50: score+=1
    if oos_pass: score+=3
    if cross_asset_hits>=2: score+=1
    if cross_tf_hits>=2: score+=1
    score-=decay_penalty

    status="REJECTED"
    if score>=8 and oos_pass:
        status="INSTITUTIONAL_CANDIDATE"
    elif score>=6 and oos_pass:
        status="RESEARCH_CANDIDATE"

    item=dict(e)
    item.update({
        "regime":regime(e),
        "validation_score":score,
        "cross_asset_hits":cross_asset_hits,
        "cross_timeframe_hits":cross_tf_hits,
        "local_family_hits":local_family_hits,
        "decay_penalty":decay_penalty,
        "out_of_sample_pass":bool(oos_pass),
        "final_status":status,
        "live":"FORBIDDEN",
        "real_orders":"FORBIDDEN"
    })
    return item

def build_memory(validated):
    memory=load(MEM,[])
    now=datetime.now(UTC).isoformat()
    for e in validated:
        memory.append({
            "created_at":now,
            "asset":e.get("symbol"),
            "timeframe":e.get("timeframe"),
            "strategy":e.get("strategy"),
            "fast":e.get("fast"),
            "slow":e.get("slow"),
            "regime":e.get("regime"),
            "profit_factor":e.get("profit_factor"),
            "trades":e.get("trades"),
            "winrate":e.get("winrate"),
            "total_return":e.get("total_return"),
            "validation_score":e.get("validation_score"),
            "final_status":e.get("final_status"),
            "source":"P15.17_EDGE_VALIDATION_MEGA_PACK"
        })
    MEM.parent.mkdir(parents=True,exist_ok=True)
    MEM.write_text(json.dumps(memory,indent=2,ensure_ascii=False),encoding="utf-8")
    return memory

def web_research_queue_summary():
    q=load(QUEUE,[])
    fam=Counter(x.get("family") for x in q)
    assets=Counter(x.get("asset") for x in q)
    return {
        "queue_items":len(q),
        "families":fam.most_common(),
        "assets":assets.most_common(),
        "mode":"WEB_STRATEGY_CONTINUOUS_RESEARCH_AS_HYPOTHESIS_ONLY",
        "requires_backtest":True
    }

def run():
    auth=load(AUTH,[])
    all_rows=load(ALL,[])
    validated=[validate_edge(e,all_rows) for e in auth]
    validated.sort(key=lambda x:(x["final_status"]=="INSTITUTIONAL_CANDIDATE",x["validation_score"],x.get("profit_factor",0)), reverse=True)

    approved=[x for x in validated if x["final_status"]=="INSTITUTIONAL_CANDIDATE"]
    research=[x for x in validated if x["final_status"]=="RESEARCH_CANDIDATE"]
    rejected=[x for x in validated if x["final_status"]=="REJECTED"]
    memory=build_memory(validated)

    out=Path("reports/P15.17_EDGE_VALIDATION_MEGA_PACK")
    out.mkdir(parents=True,exist_ok=True)

    report={
        "STATUS":"P15.17_EDGE_VALIDATION_MEGA_PACK_IMPLEMENTED",
        "INPUT_AUTHORITY_EDGES":len(auth),
        "VALIDATED":len(validated),
        "INSTITUTIONAL_CANDIDATES":len(approved),
        "RESEARCH_CANDIDATES":len(research),
        "REJECTED":len(rejected),
        "TOP_REGIMES":Counter(x["regime"] for x in validated).most_common(),
        "WEB_STRATEGY_CONTINUOUS_RESEARCH":web_research_queue_summary(),
        "EDGE":"INSTITUTIONAL_CANDIDATE_FOUND" if approved else ("RESEARCH_CANDIDATE_FOUND" if research else "NOT_PROVEN"),
        "CAUSALITY":"NOT_PROVEN",
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "NEXT":"P15.18_PAPER_RESEARCH_PORTFOLIO_SIMULATOR",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (out/"final_rank.json").write_text(json.dumps(validated,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"approved_edges.json").write_text(json.dumps(approved,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"research_edges.json").write_text(json.dumps(research,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"rejected_edges.json").write_text(json.dumps(rejected,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"edge_memory.json").write_text(json.dumps(memory,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"institutional_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))

import json
from pathlib import Path
from datetime import datetime, UTC

SPECIALISTS = Path("reports/P1610_SPECIALIST_LIBRARY/specialist_library.json")
PAYOFF = Path("reports/P1628_PAYOFF_FORENSICS_ENGINE/p1628_payoff_forensics.json")
OPPS = Path("reports/P1637_SESSION_AND_THRESHOLD_REFINEMENT/refined_opportunity_ranking.json")
OUT = Path("reports/P1700_ELITE_SELECTION_PROGRAM")
REPORT = OUT / "p1701_to_p1710_elite_selection_report.json"

def load(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []

specialists = load(SPECIALISTS)
payoff = load(PAYOFF)
opps = load(OPPS)

payoff_map = {p.get("edge_id"): p for p in payoff}
opp_map = {o.get("specialist_id"): o for o in opps}

elite_rows = []

for s in specialists:
    edge_id = s.get("edge_id")
    specialist_id = s.get("specialist_id")

    p = payoff_map.get(edge_id, {})
    o = opp_map.get(specialist_id, {})

    payoff_ratio = float(s.get("payoff_ratio_real") or 0)
    expectancy = float(s.get("expectancy_per_trade_real") or 0)
    pf = float(s.get("profit_factor_real") or 0)
    deployment = float(s.get("deployment_score") or 0)
    confluence = float(o.get("confluence_score") or 0)
    refined = float(o.get("refined_opportunity_score") or 0)
    avg_r = float(p.get("avg_R") or 0)
    max_r = float(p.get("max_R") or 0)

    elite_score = (
        payoff_ratio * 2.0 +
        expectancy * 100 +
        pf * 1.2 +
        deployment * 0.5 +
        confluence * 0.4 +
        refined * 0.4 +
        avg_r * 1.5 +
        max_r * 0.5
    )

    if elite_score >= 100:
        tier = "A_PLUS"
    elif elite_score >= 75:
        tier = "A"
    elif elite_score >= 50:
        tier = "B"
    elif elite_score >= 30:
        tier = "C"
    else:
        tier = "D"

    elite_rows.append({
        "specialist_id": specialist_id,
        "edge_id": edge_id,
        "asset": s.get("asset"),
        "timeframe": s.get("timeframe"),
        "family": s.get("family"),
        "profile": s.get("profile"),
        "payoff_ratio": payoff_ratio,
        "expectancy": expectancy,
        "profit_factor": pf,
        "deployment_score": deployment,
        "confluence_score": confluence,
        "refined_opportunity_score": refined,
        "avg_R": avg_r,
        "max_R": max_r,
        "elite_score": round(elite_score, 6),
        "tier": tier,
        "survival_status": "KEEP" if tier in ["A_PLUS","A","B"] else "WATCH_OR_QUARANTINE",
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    })

elite_rows = sorted(elite_rows, key=lambda x: x["elite_score"], reverse=True)

top20 = elite_rows[:20]
top10 = elite_rows[:10]
top5 = elite_rows[:5]

asset_dna = {}
for r in elite_rows:
    a = r["asset"]
    asset_dna.setdefault(a, {
        "asset": a,
        "specialists": 0,
        "top_specialists": [],
        "best_elite_score": 0,
        "best_payoff": 0,
        "best_pf": 0,
        "best_expectancy": 0
    })
    asset_dna[a]["specialists"] += 1
    asset_dna[a]["best_elite_score"] = max(asset_dna[a]["best_elite_score"], r["elite_score"])
    asset_dna[a]["best_payoff"] = max(asset_dna[a]["best_payoff"], r["payoff_ratio"])
    asset_dna[a]["best_pf"] = max(asset_dna[a]["best_pf"], r["profit_factor"])
    asset_dna[a]["best_expectancy"] = max(asset_dna[a]["best_expectancy"], r["expectancy"])
    if len(asset_dna[a]["top_specialists"]) < 5:
        asset_dna[a]["top_specialists"].append(r["specialist_id"])

no_trade_filters = []
for r in elite_rows:
    reasons = []
    if r["refined_opportunity_score"] < 60:
        reasons.append("LOW_REFINED_OPPORTUNITY_SCORE")
    if r["confluence_score"] < 60:
        reasons.append("LOW_CONFLUENCE")
    if r["elite_score"] < 30:
        reasons.append("LOW_ELITE_SCORE")
    if r["expectancy"] <= 0:
        reasons.append("NON_POSITIVE_EXPECTANCY")

    if reasons:
        no_trade_filters.append({
            "specialist_id": r["specialist_id"],
            "asset": r["asset"],
            "timeframe": r["timeframe"],
            "family": r["family"],
            "no_trade_reasons": reasons,
            "action": "DO_NOT_OPERATE_UNLESS_CONTEXT_IMPROVES"
        })

master_decision = {
    "best_specialist": top5[0] if top5 else None,
    "decision": "WATCH_ONLY",
    "reason": "ELITE_SELECTION_CREATED_BUT_REAL_ORDERS_FORBIDDEN_AND_THRESHOLD_NOT_CONFIRMED",
    "minimum_operational_threshold": 80,
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN"
}

report = {
    "STATUS": "P1701_TO_P1710_ELITE_SELECTION_COMPLETED",
    "SPECIALISTS_INPUT": len(specialists),
    "TOP20_CREATED": len(top20),
    "TOP10_CREATED": len(top10),
    "TOP5_CREATED": len(top5),
    "A_PLUS": len([x for x in elite_rows if x["tier"] == "A_PLUS"]),
    "A": len([x for x in elite_rows if x["tier"] == "A"]),
    "B": len([x for x in elite_rows if x["tier"] == "B"]),
    "C": len([x for x in elite_rows if x["tier"] == "C"]),
    "D": len([x for x in elite_rows if x["tier"] == "D"]),
    "TOP20": top20,
    "TOP10": top10,
    "TOP5": top5,
    "ASSET_DNA": list(asset_dna.values()),
    "NO_TRADE_FILTERS": no_trade_filters[:50],
    "MASTER_DECISION": master_decision,
    "NEXT": "P1711_EDGE_AGING_AND_CYCLE_MATCHING_ENGINE",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(OUT / "elite_specialist_ranking.json").write_text(json.dumps(elite_rows, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "elite_top20.json").write_text(json.dumps(top20, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "elite_top10.json").write_text(json.dumps(top10, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "asset_dna.json").write_text(json.dumps(list(asset_dna.values()), indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "no_trade_filters.json").write_text(json.dumps(no_trade_filters, indent=2, ensure_ascii=False), encoding="utf-8")
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "STATUS": report["STATUS"],
    "SPECIALISTS_INPUT": report["SPECIALISTS_INPUT"],
    "TOP20_CREATED": report["TOP20_CREATED"],
    "TOP10_CREATED": report["TOP10_CREATED"],
    "TOP5_CREATED": report["TOP5_CREATED"],
    "A_PLUS": report["A_PLUS"],
    "A": report["A"],
    "B": report["B"],
    "NEXT": report["NEXT"],
    "REAL_ORDERS": "FORBIDDEN"
}, indent=2, ensure_ascii=False))

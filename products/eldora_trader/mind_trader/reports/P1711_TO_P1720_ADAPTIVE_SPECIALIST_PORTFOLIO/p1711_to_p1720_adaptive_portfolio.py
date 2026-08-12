import json
from pathlib import Path
from datetime import datetime, UTC
from collections import defaultdict

BASE = Path("reports/P1711_TO_P1720_ADAPTIVE_SPECIALIST_PORTFOLIO")
ELITE = Path("reports/P1700_ELITE_SELECTION_PROGRAM/elite_specialist_ranking.json")
ASSET_DNA = Path("reports/P1700_ELITE_SELECTION_PROGRAM/asset_dna.json")
CONF = Path("reports/P1620_CONFLUENCE_ENGINE/confluence_snapshot.json")
PAYOFF = Path("reports/P1628_PAYOFF_FORENSICS_ENGINE/p1628_payoff_forensics.json")

def load(p, default=[]):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

elite = load(ELITE)
asset_dna = load(ASSET_DNA)
conf = load(CONF)
payoff = load(PAYOFF)

payoff_map = {p.get("edge_id"): p for p in payoff}
conf_map = {(c.get("asset"), c.get("timeframe")): c for c in conf}

portfolio = []
cycle_library = []
activation = []
capital = []
fatigue = []
payoff_max = []
asset_dna_v2 = []

for e in elite:
    p = payoff_map.get(e.get("edge_id"), {})
    c = conf_map.get((e.get("asset"), e.get("timeframe")), {})

    elite_score = float(e.get("elite_score") or 0)
    avg_r = float(e.get("avg_R") or 0)
    max_r = float(e.get("max_R") or 0)
    confluence = float(e.get("confluence_score") or 0)
    refined = float(e.get("refined_opportunity_score") or 0)

    edge_health = min(100, elite_score * 0.45 + confluence * 0.25 + refined * 0.20 + avg_r * 2)

    if edge_health >= 80:
        status = "ACTIVE_ELITE"
    elif edge_health >= 60:
        status = "ACTIVE"
    elif edge_health >= 40:
        status = "WATCH"
    else:
        status = "SUSPEND"

    if e.get("family") in ["EMA_CROSS","SMA_CROSS","ATR_TREND"]:
        best_phase = ["TREND", "EXPANSION"]
    elif e.get("family") in ["RSI_REVERSION","BOLLINGER_REVERSION"]:
        best_phase = ["RANGE", "MEAN_REVERSION"]
    else:
        best_phase = ["BREAKOUT", "VOLATILITY_EXPANSION"]

    portfolio.append({
        "specialist_id": e.get("specialist_id"),
        "asset": e.get("asset"),
        "timeframe": e.get("timeframe"),
        "family": e.get("family"),
        "profile": e.get("profile"),
        "elite_score": elite_score,
        "edge_health": round(edge_health, 6),
        "status": status,
        "best_market_phase": best_phase,
        "avg_R": avg_r,
        "max_R": max_r,
        "confluence_score": confluence,
        "refined_opportunity_score": refined,
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    })

    fatigue_status = "NORMAL"
    if confluence < 40 and refined < 50:
        fatigue_status = "CONTEXT_WEAK"
    if elite_score > 100 and confluence < 30:
        fatigue_status = "ELITE_EDGE_WAIT_FOR_CONTEXT"

    fatigue.append({
        "specialist_id": e.get("specialist_id"),
        "asset": e.get("asset"),
        "fatigue_status": fatigue_status,
        "reason": "CONTEXT_BASED_NOT_PERFORMANCE_DECAY",
        "action": "WAIT_OR_REDUCE" if fatigue_status != "NORMAL" else "KEEP"
    })

    payoff_max.append({
        "specialist_id": e.get("specialist_id"),
        "asset": e.get("asset"),
        "avg_R": avg_r,
        "max_R": max_r,
        "p50_R": p.get("p50_R"),
        "p80_R": p.get("p80_R"),
        "p90_R": p.get("p90_R"),
        "runner_policy": "NO_EARLY_PARTIAL" if max_r >= 5 else "STANDARD_MANAGEMENT",
        "payoff_objective": "MAXIMIZE_R_PER_TRADE"
    })

portfolio = sorted(portfolio, key=lambda x: x["edge_health"], reverse=True)

active = [x for x in portfolio if x["status"] in ["ACTIVE_ELITE","ACTIVE"]]
total_health = sum(x["edge_health"] for x in active) or 1

for x in active[:10]:
    allocation = x["edge_health"] / total_health
    capital.append({
        "specialist_id": x["specialist_id"],
        "asset": x["asset"],
        "timeframe": x["timeframe"],
        "status": x["status"],
        "edge_health": x["edge_health"],
        "capital_weight": round(allocation, 6),
        "suggested_mode": "DEMO_RESEARCH_ONLY",
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    })

for a in asset_dna:
    asset_dna_v2.append({
        **a,
        "asset_dna_v2_status": "ACTIVE",
        "best_market_phase": "DERIVED_FROM_TOP_SPECIALISTS",
        "capital_priority": "HIGH" if a.get("best_elite_score",0) >= 100 else "MEDIUM",
        "memory_note": "CYCLE_AND_CONTEXT_AWARE_ASSET_PROFILE"
    })

master = {
    "STATUS": "P1711_TO_P1720_ADAPTIVE_SPECIALIST_PORTFOLIO_COMPLETED",
    "SPECIALISTS_INPUT": len(elite),
    "PORTFOLIO_SPECIALISTS": len(portfolio),
    "ACTIVE_SPECIALISTS": len(active),
    "CAPITAL_ALLOCATIONS": len(capital),
    "TOP5_ACTIVE": portfolio[:5],
    "CAPITAL_ALLOCATION_TOP": capital[:10],
    "NEXT": "P1721_REAL_MTF_LINK_AND_CONTEXTUAL_BACKTEST_REVALIDATION",
    "DECISION": "DEMO_RESEARCH_ONLY",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(BASE/"adaptive_specialist_portfolio.json").write_text(json.dumps(portfolio, indent=2, ensure_ascii=False), encoding="utf-8")
(BASE/"capital_allocation.json").write_text(json.dumps(capital, indent=2, ensure_ascii=False), encoding="utf-8")
(BASE/"specialist_fatigue.json").write_text(json.dumps(fatigue, indent=2, ensure_ascii=False), encoding="utf-8")
(BASE/"payoff_maximizer.json").write_text(json.dumps(payoff_max, indent=2, ensure_ascii=False), encoding="utf-8")
(BASE/"asset_dna_v2.json").write_text(json.dumps(asset_dna_v2, indent=2, ensure_ascii=False), encoding="utf-8")
(BASE/"p1711_to_p1720_master_report.json").write_text(json.dumps(master, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(master, indent=2, ensure_ascii=False))

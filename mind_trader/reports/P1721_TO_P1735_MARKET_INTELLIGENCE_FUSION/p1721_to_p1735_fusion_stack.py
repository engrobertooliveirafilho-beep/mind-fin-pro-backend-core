import json
from pathlib import Path
from datetime import datetime, UTC
from collections import defaultdict

BASE = Path("reports/P1721_TO_P1735_MARKET_INTELLIGENCE_FUSION")

SPECIALISTS = Path("reports/P1711_TO_P1720_ADAPTIVE_SPECIALIST_PORTFOLIO/adaptive_specialist_portfolio.json")
CONF = Path("reports/P1620_CONFLUENCE_ENGINE/confluence_snapshot.json")
PAYOFF = Path("reports/P1628_PAYOFF_FORENSICS_ENGINE/p1628_payoff_forensics.json")
CANDLES = Path("reports/P1619_CANDLE_TRIGGER_ENGINE/candle_trigger_snapshot.json")
STRUCTURE = Path("reports/P1618_MARKET_STRUCTURE_ENGINE/market_structure_snapshot.json")
SESSIONS = Path("reports/P1637_SESSION_AND_THRESHOLD_REFINEMENT/refined_session_library.json")

def load(p, default=[]):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

specialists = load(SPECIALISTS)
conf = load(CONF)
payoff = load(PAYOFF)
candles = load(CANDLES)
structure = load(STRUCTURE)
sessions = load(SESSIONS)

conf_map = {(x.get("asset"), x.get("timeframe")): x for x in conf}
payoff_map = {x.get("edge_id"): x for x in payoff}
candle_map = {(x.get("asset"), x.get("timeframe")): x for x in candles}
structure_map = {(x.get("asset"), x.get("timeframe")): x for x in structure}

fusion = []
coalitions = []
asset_memory = defaultdict(lambda: {
    "asset": None,
    "specialists": 0,
    "best_execution_score": 0,
    "best_family": None,
    "best_profile": None,
    "dominant_phases": defaultdict(int),
    "dominant_timeframes": defaultdict(int)
})

for s in specialists:
    asset = s.get("asset")
    tf = s.get("timeframe")
    edge_id = s.get("edge_id")
    sid = s.get("specialist_id")

    c = conf_map.get((asset, tf), {})
    p = payoff_map.get(edge_id, {})
    cd = candle_map.get((asset, tf), {})
    st = structure_map.get((asset, tf), {})

    edge_health = float(s.get("edge_health") or 0)
    elite_score = float(s.get("elite_score") or 0)
    confluence = float(c.get("confluence_score") or s.get("confluence_score") or 0)
    avg_r = float(s.get("avg_R") or p.get("avg_R") or 0)
    max_r = float(s.get("max_R") or p.get("max_R") or 0)

    mtf_score = min(100, confluence + (10 if tf in ["H4","D1"] else 0))

    candle_score = float(cd.get("candle_score") or 0)
    structure_score = float(st.get("structure_score") or 0)

    payoff_cluster = "LOW_R"
    if max_r >= 20:
        payoff_cluster = "TAIL_20R_PLUS"
    elif max_r >= 10:
        payoff_cluster = "TAIL_10R_PLUS"
    elif max_r >= 5:
        payoff_cluster = "TAIL_5R_PLUS"
    elif max_r >= 2:
        payoff_cluster = "NORMAL_2R_PLUS"

    family = s.get("family")
    if family in ["EMA_CROSS","SMA_CROSS","ATR_TREND"]:
        regime_fit = "TREND_EXPANSION"
        regime_score = 80
    elif family in ["RSI_REVERSION","BOLLINGER_REVERSION"]:
        regime_fit = "RANGE_MEAN_REVERSION"
        regime_score = 80
    else:
        regime_fit = "BREAKOUT_VOLATILITY"
        regime_score = 75

    session_score = 50
    hour = c.get("hour")
    if hour is not None:
        h = int(hour)
        if 7 <= h <= 16:
            session_score = 75
        elif 17 <= h <= 20:
            session_score = 70
        else:
            session_score = 45

    execution_score = min(100, (
        edge_health * 0.25 +
        elite_score * 0.20 +
        mtf_score * 0.15 +
        structure_score * 0.10 +
        candle_score * 0.10 +
        regime_score * 0.10 +
        session_score * 0.05 +
        min(100, avg_r * 10) * 0.05
    ))

    if execution_score >= 90:
        decision = "ELITE_EXECUTION_CANDIDATE"
    elif execution_score >= 80:
        decision = "DEMO_EXECUTION_CANDIDATE"
    elif execution_score >= 70:
        decision = "HIGH_PRIORITY_WATCH"
    else:
        decision = "WATCH_ONLY"

    row = {
        "specialist_id": sid,
        "asset": asset,
        "timeframe": tf,
        "family": family,
        "profile": s.get("profile"),
        "mtf_alignment_score": round(mtf_score, 6),
        "market_regime_fit": regime_fit,
        "structure_score": structure_score,
        "candle_score": candle_score,
        "session_score": session_score,
        "avg_R": avg_r,
        "max_R": max_r,
        "payoff_cluster": payoff_cluster,
        "edge_health": edge_health,
        "elite_score": elite_score,
        "execution_score": round(execution_score, 6),
        "decision": decision,
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    }

    fusion.append(row)

    a = asset_memory[asset]
    a["asset"] = asset
    a["specialists"] += 1
    a["best_execution_score"] = max(a["best_execution_score"], execution_score)
    if execution_score >= a["best_execution_score"]:
        a["best_family"] = family
        a["best_profile"] = s.get("profile")
    a["dominant_phases"][regime_fit] += 1
    a["dominant_timeframes"][tf] += 1

fusion = sorted(fusion, key=lambda x: x["execution_score"], reverse=True)

by_asset = defaultdict(list)
for f in fusion:
    by_asset[f["asset"]].append(f)

for asset, rows in by_asset.items():
    top = rows[:3]
    consensus_score = sum(x["execution_score"] for x in top) / max(len(top), 1)
    coalitions.append({
        "asset": asset,
        "coalition_size": len(top),
        "specialists": [x["specialist_id"] for x in top],
        "families": list(sorted(set(x["family"] for x in top))),
        "profiles": list(sorted(set(x["profile"] for x in top))),
        "consensus_score": round(consensus_score, 6),
        "coalition_decision": "COALITION_ACTIVE" if consensus_score >= 75 else "COALITION_WATCH",
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    })

asset_memory_rows = []
for asset, a in asset_memory.items():
    asset_memory_rows.append({
        "asset": asset,
        "specialists": a["specialists"],
        "best_execution_score": round(a["best_execution_score"], 6),
        "best_family": a["best_family"],
        "best_profile": a["best_profile"],
        "dominant_phases": dict(a["dominant_phases"]),
        "dominant_timeframes": dict(a["dominant_timeframes"]),
        "memory_status": "ASSET_MEMORY_REGISTERED"
    })

master = {
    "STATUS": "P1721_TO_P1735_MARKET_INTELLIGENCE_FUSION_COMPLETED",
    "SPECIALISTS_INPUT": len(specialists),
    "FUSION_ROWS": len(fusion),
    "COALITIONS_CREATED": len(coalitions),
    "ASSET_MEMORY_ROWS": len(asset_memory_rows),
    "ELITE_EXECUTION_CANDIDATES": len([x for x in fusion if x["decision"] == "ELITE_EXECUTION_CANDIDATE"]),
    "DEMO_EXECUTION_CANDIDATES": len([x for x in fusion if x["decision"] == "DEMO_EXECUTION_CANDIDATE"]),
    "HIGH_PRIORITY_WATCH": len([x for x in fusion if x["decision"] == "HIGH_PRIORITY_WATCH"]),
    "TOP10_EXECUTION": fusion[:10],
    "TOP_COALITIONS": sorted(coalitions, key=lambda x: x["consensus_score"], reverse=True)[:10],
    "NEXT": "P1736_MASTER_EXECUTION_BRAIN_V2_AND_DAILY_ORCHESTRATOR_PATCH",
    "DECISION": "DEMO_RESEARCH_ONLY",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(BASE/"market_intelligence_fusion.json").write_text(json.dumps(fusion, indent=2, ensure_ascii=False), encoding="utf-8")
(BASE/"specialist_coalitions.json").write_text(json.dumps(coalitions, indent=2, ensure_ascii=False), encoding="utf-8")
(BASE/"asset_memory_engine.json").write_text(json.dumps(asset_memory_rows, indent=2, ensure_ascii=False), encoding="utf-8")
(BASE/"p1721_to_p1735_master_report.json").write_text(json.dumps(master, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(master, indent=2, ensure_ascii=False))

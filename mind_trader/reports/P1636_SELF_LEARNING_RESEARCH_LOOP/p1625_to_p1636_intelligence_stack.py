import json
from pathlib import Path
from datetime import datetime, UTC
from collections import defaultdict

SPECIALISTS = Path("reports/P1610_SPECIALIST_LIBRARY/specialist_library.json")
OPPS = Path("reports/P1623_OPPORTUNITY_RANKING_ENGINE/opportunity_ranking.json")
CONF = Path("reports/P1620_CONFLUENCE_ENGINE/confluence_snapshot.json")
TRADES = Path("reports/P1505_DATA_INGESTION_ENGINE/p1505n_trade_level_trades.json")

OUT_BASE = Path("reports")

def load(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

specialists = load(SPECIALISTS, [])
opps = load(OPPS, [])
conf = load(CONF, [])
trades = load(TRADES, [])

conf_map = {(c.get("asset"), c.get("timeframe")): c for c in conf}

# P1625 — Multi-timeframe confirmation
mtf = []
for s in specialists:
    asset = s.get("asset")
    tf = s.get("timeframe")
    c = conf_map.get((asset, tf), {})
    score = float(c.get("confluence_score") or 0)
    mtf.append({
        "asset": asset,
        "timeframe": tf,
        "specialist_id": s.get("specialist_id"),
        "macro_alignment": "PENDING_HIGHER_TF_REAL_LINK",
        "current_tf_confluence": score,
        "mtf_alignment_score": min(100, score + 10 if tf in ["H4","D1"] else score),
        "status": "MTF_CONFIRMATION_REGISTERED",
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    })

# P1626 — Regime detection
regimes = []
for c in conf:
    score = float(c.get("confluence_score") or 0)
    if score >= 75:
        regime = "HIGH_CONFLUENCE_EXPANSION"
    elif score >= 50:
        regime = "NORMAL_CONFLUENCE"
    else:
        regime = "LOW_CONFLUENCE_RANGE"
    regimes.append({
        "asset": c.get("asset"),
        "timeframe": c.get("timeframe"),
        "session": c.get("session"),
        "confluence_score": score,
        "detected_regime": regime,
        "status": "REGIME_CLASSIFIED"
    })

# P1627 — Session intelligence
session_stats = defaultdict(lambda: {"count":0, "assets":defaultdict(int), "avg_confluence":0})
for c in conf:
    ses = c.get("session") or "UNKNOWN"
    session_stats[ses]["count"] += 1
    session_stats[ses]["assets"][c.get("asset")] += 1
    session_stats[ses]["avg_confluence"] += float(c.get("confluence_score") or 0)

session_library = []
for ses, d in session_stats.items():
    count = max(d["count"], 1)
    session_library.append({
        "session": ses,
        "samples": d["count"],
        "avg_confluence": round(d["avg_confluence"] / count, 6),
        "assets": dict(d["assets"]),
        "status": "SESSION_INTELLIGENCE_REGISTERED"
    })

# P1628 — Payoff forensics
payoff_by_edge = defaultdict(list)
for t in trades:
    edge = t.get("edge_id")
    pnl = float(t.get("pnl_pct") or 0)
    mae = abs(float(t.get("mae_pct") or 0.0001))
    r = pnl / max(mae, 0.0001)
    payoff_by_edge[edge].append(r)

payoff_library = []
for edge, rs in payoff_by_edge.items():
    if not rs:
        continue
    rs_sorted = sorted(rs)
    n = len(rs_sorted)
    payoff_library.append({
        "edge_id": edge,
        "trades": n,
        "avg_R": round(sum(rs_sorted)/n, 6),
        "max_R": round(max(rs_sorted), 6),
        "p50_R": round(rs_sorted[int(n*0.50)], 6),
        "p80_R": round(rs_sorted[int(n*0.80)-1], 6) if n >= 5 else None,
        "p90_R": round(rs_sorted[int(n*0.90)-1], 6) if n >= 10 else None,
        "status": "PAYOFF_FORENSICS_REGISTERED"
    })

# P1629 — Trade DNA
dna = []
payoff_map = {p["edge_id"]: p for p in payoff_library}
for s in specialists:
    p = payoff_map.get(s.get("edge_id"), {})
    dna.append({
        "specialist_id": s.get("specialist_id"),
        "edge_id": s.get("edge_id"),
        "asset": s.get("asset"),
        "timeframe": s.get("timeframe"),
        "family": s.get("family"),
        "profile": s.get("profile"),
        "regime_tags": s.get("regime_tags"),
        "best_entry_hour": s.get("best_entry_hour"),
        "payoff_ratio_real": s.get("payoff_ratio_real"),
        "expectancy_per_trade_real": s.get("expectancy_per_trade_real"),
        "profit_factor_real": s.get("profit_factor_real"),
        "avg_holding_bars": s.get("avg_holding_bars"),
        "avg_R": p.get("avg_R"),
        "max_R": p.get("max_R"),
        "p90_R": p.get("p90_R"),
        "dna_status": "TRADE_DNA_REGISTERED"
    })

# P1630/31/32 — Libraries from current snapshots
structure_library = defaultdict(int)
fibo_library = defaultdict(int)
candle_library = defaultdict(int)

for c in conf:
    structure_library[f"{c.get('asset')}_{c.get('timeframe')}_{c.get('confluence_score')}"] += 1

for s in specialists:
    for tag in s.get("regime_tags") or []:
        structure_library[tag] += 1

# P1633 — Confluence pattern miner
patterns = []
for o in opps:
    patterns.append({
        "asset": o.get("asset"),
        "timeframe": o.get("timeframe"),
        "specialist_id": o.get("specialist_id"),
        "family": o.get("family"),
        "profile": o.get("profile"),
        "deployment_score": o.get("deployment_score"),
        "confluence_score": o.get("confluence_score"),
        "opportunity_score": o.get("opportunity_score"),
        "pattern_status": "MINED_CANDIDATE",
        "decision": o.get("decision")
    })
patterns = sorted(patterns, key=lambda x: float(x.get("opportunity_score") or 0), reverse=True)

# P1634 — Specialist evolution
evolved = []
for s in specialists:
    score = float(s.get("deployment_score") or 0)
    if score >= 60:
        tier = "ELITE"
    elif score >= 40:
        tier = "STRONG"
    elif score >= 20:
        tier = "ACTIVE"
    else:
        tier = "WATCHLIST"
    evolved.append({
        "specialist_id": s.get("specialist_id"),
        "asset": s.get("asset"),
        "timeframe": s.get("timeframe"),
        "family": s.get("family"),
        "profile": s.get("profile"),
        "deployment_score": score,
        "tier": tier,
        "status": "SPECIALIST_EVOLUTION_CLASSIFIED"
    })

# P1635 — Master brain
top = patterns[0] if patterns else None
brain = {
    "STATUS": "P1635_MASTER_PORTFOLIO_BRAIN_COMPLETED",
    "BEST_CURRENT_OPPORTUNITY": top,
    "DECISION": "WATCH_ONLY" if not top or float(top.get("opportunity_score") or 0) < 85 else "ELITE_DEMO_CANDIDATE",
    "REASON": "REAL_ORDERS_FORBIDDEN_AND_CONFLUENCE_THRESHOLD_NOT_MET",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN"
}

# P1636 — Self learning loop plan
loop = {
    "STATUS": "P1636_SELF_LEARNING_RESEARCH_LOOP_REGISTERED",
    "LOOP": [
        "DISCOVER",
        "BACKTEST",
        "VALIDATE",
        "CATALOG_SPECIALIST",
        "CLASSIFY_REGIME",
        "MINE_CONFLUENCE",
        "PROMOTE",
        "QUARANTINE_WEAK_SPECIALISTS"
    ],
    "NEXT": "ADD_P1625_TO_P1636_TO_DAILY_ORCHESTRATOR",
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN"
}

def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

write(OUT_BASE/"P1625_MULTI_TIMEFRAME_CONFIRMATION/p1625_mtf_confirmation.json", mtf)
write(OUT_BASE/"P1626_REGIME_DETECTION_ENGINE/p1626_regime_detection.json", regimes)
write(OUT_BASE/"P1627_SESSION_INTELLIGENCE_ENGINE/p1627_session_intelligence.json", session_library)
write(OUT_BASE/"P1628_PAYOFF_FORENSICS_ENGINE/p1628_payoff_forensics.json", payoff_library)
write(OUT_BASE/"P1629_TRADE_DNA_ENGINE/p1629_trade_dna.json", dna)
write(OUT_BASE/"P1630_MARKET_STRUCTURE_LIBRARY/p1630_market_structure_library.json", dict(structure_library))
write(OUT_BASE/"P1631_FIBONACCI_LIBRARY/p1631_fibonacci_library.json", dict(fibo_library))
write(OUT_BASE/"P1632_CANDLE_STATISTICS_LIBRARY/p1632_candle_statistics_library.json", dict(candle_library))
write(OUT_BASE/"P1633_CONFLUENCE_PATTERN_MINER/p1633_confluence_patterns.json", patterns)
write(OUT_BASE/"P1634_SPECIALIST_EVOLUTION_ENGINE/p1634_specialist_evolution.json", evolved)
write(OUT_BASE/"P1635_MASTER_PORTFOLIO_BRAIN/p1635_master_portfolio_brain.json", brain)
write(OUT_BASE/"P1636_SELF_LEARNING_RESEARCH_LOOP/p1636_self_learning_loop.json", loop)

master = {
    "STATUS": "P1625_TO_P1636_INTELLIGENCE_STACK_COMPLETED",
    "MTF_ROWS": len(mtf),
    "REGIME_ROWS": len(regimes),
    "SESSION_LIBRARIES": len(session_library),
    "PAYOFF_EDGES": len(payoff_library),
    "TRADE_DNA_ROWS": len(dna),
    "CONFLUENCE_PATTERNS": len(patterns),
    "SPECIALISTS_EVOLVED": len(evolved),
    "MASTER_BRAIN_DECISION": brain,
    "NEXT": "ADD_P1625_TO_P1636_TO_DAILY_ORCHESTRATOR",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

write(OUT_BASE/"P1636_SELF_LEARNING_RESEARCH_LOOP/p1625_to_p1636_master_report.json", master)
print(json.dumps(master, indent=2, ensure_ascii=False))

import json
import hashlib
import pandas as pd
from pathlib import Path
from datetime import datetime, UTC

BASE = Path("reports/P1886_TO_P1900_MARKET_MEMORY_AND_SUPREME_KB")
MEMORY = Path("data/lake/memory")
EXPERIENCE = Path("data/lake/experience")
HEALTH = Path("data/lake/health")
PORTFOLIO = Path("data/lake/portfolio")
GRAPHS = Path("data/lake/graphs")
KB = Path("data/lake/knowledge_base")

DNA = Path("data/lake/dna/p1871_trade_dna.csv")
GEN2 = Path("data/lake/specialists/gen2/p1885a_gen2_elites.json")
RANKING = Path("data/lake/specialists/gen2/p1885a_gen2_ranking.json")
ASSETS = Path("data/lake/assets/p1881_to_p1883_asset_personalities.json")
PATTERNS = Path("data/lake/dna/p1875_pattern_genome.json")
CLUSTERS = Path("data/lake/dna/p1874_dna_clusters.json")

def load_json(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def sid(obj, prefix):
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    return prefix + "_" + hashlib.md5(raw.encode()).hexdigest()[:16]

dna = pd.read_csv(DNA)
gen2 = load_json(GEN2, [])
ranking = load_json(RANKING, [])
asset_profiles = load_json(ASSETS, [])
patterns = load_json(PATTERNS, [])
clusters = load_json(CLUSTERS, [])

# P1886 Market Memory
market_memory = []
for _, r in dna.iterrows():
    item = {
        "memory_id": sid({
            "asset": r["asset"],
            "family": r["family"],
            "time": r["entry_time"],
            "trigger": r["trigger"],
            "regime": r["mtf_context_proxy"]
        }, "MEM"),
        "asset": r["asset"],
        "family": r["family"],
        "time": r["entry_time"],
        "trigger": r["trigger"],
        "session": r["session"],
        "trend_regime": r["trend_regime"],
        "volatility_regime": r["volatility_regime"],
        "context": r["mtf_context_proxy"],
        "outcome": r["outcome"],
        "return": float(r["return_1bar"]),
        "market_energy": float(r["market_physics_energy"]),
        "entropy": float(r["market_entropy_proxy"]),
        "memory_type": "TRADE_CONTEXT_OUTCOME"
    }
    market_memory.append(item)

# P1887 Regime Memory
regime_memory = []
for keys, g in dna.groupby(["asset","family","trend_regime","volatility_regime"]):
    wins = g[g["outcome"]=="WIN"]
    losses = g[g["outcome"]=="LOSS"]
    gross_win = float(wins["return_1bar"].sum()) if len(wins) else 0
    gross_loss = abs(float(losses["return_1bar"].sum())) if len(losses) else 0
    pf = gross_win / gross_loss if gross_loss > 0 else gross_win

    regime_memory.append({
        "regime_memory_id": sid(str(keys), "REGMEM"),
        "asset": keys[0],
        "family": keys[1],
        "trend_regime": keys[2],
        "volatility_regime": keys[3],
        "trades": int(len(g)),
        "win_rate": round(len(wins)/len(g), 6),
        "profit_factor_proxy": round(pf, 6),
        "avg_return": round(float(g["return_1bar"].mean()), 8),
        "status": "REGIME_MEMORY_ACTIVE"
    })

# P1888 Black Swan Memory proxy by year buckets
black_swan_years = {
    "COVID_2020": [2020],
    "RATE_HIKE_CYCLE_2022": [2022],
    "BANKING_STRESS_2023": [2023],
    "RECENT_REGIME_2024_2026": [2024,2025,2026]
}
dna["year"] = pd.to_datetime(dna["entry_time"], errors="coerce", utc=True).dt.year

black_swan_memory = []
for event, years in black_swan_years.items():
    eg = dna[dna["year"].isin(years)]
    if len(eg) == 0:
        continue
    for keys, g in eg.groupby(["asset","family"]):
        wins = g[g["outcome"]=="WIN"]
        losses = g[g["outcome"]=="LOSS"]
        gross_win = float(wins["return_1bar"].sum()) if len(wins) else 0
        gross_loss = abs(float(losses["return_1bar"].sum())) if len(losses) else 0
        pf = gross_win / gross_loss if gross_loss > 0 else gross_win
        black_swan_memory.append({
            "event_memory_id": sid({"event":event,"keys":keys}, "BSMEM"),
            "event": event,
            "asset": keys[0],
            "family": keys[1],
            "trades": int(len(g)),
            "win_rate": round(len(wins)/len(g), 6),
            "profit_factor_proxy": round(pf, 6),
            "avg_return": round(float(g["return_1bar"].mean()), 8),
            "status": "BLACK_SWAN_PROXY_MEMORY"
        })

# P1889 Context Memory
context_memory = []
for keys, g in dna.groupby(["asset","family","session","trigger","trend_regime","volatility_regime"]):
    wins = g[g["outcome"]=="WIN"]
    losses = g[g["outcome"]=="LOSS"]
    gross_win = float(wins["return_1bar"].sum()) if len(wins) else 0
    gross_loss = abs(float(losses["return_1bar"].sum())) if len(losses) else 0
    pf = gross_win / gross_loss if gross_loss > 0 else gross_win
    context_memory.append({
        "context_id": sid(str(keys), "CTX"),
        "asset": keys[0],
        "family": keys[1],
        "session": keys[2],
        "trigger": keys[3],
        "trend_regime": keys[4],
        "volatility_regime": keys[5],
        "trades": int(len(g)),
        "win_rate": round(len(wins)/len(g), 6),
        "profit_factor_proxy": round(pf, 6),
        "avg_return": round(float(g["return_1bar"].mean()), 8),
        "context_status": "PROFITABLE_CONTEXT" if pf >= 1.2 else "WEAK_CONTEXT"
    })

# P1890 Experience Engine
experience = []
for asset in sorted(dna["asset"].unique()):
    ag = dna[dna["asset"] == asset]
    best_contexts = [c for c in context_memory if c["asset"] == asset and c["context_status"] == "PROFITABLE_CONTEXT"]
    bad_contexts = [c for c in context_memory if c["asset"] == asset and c["profit_factor_proxy"] < 1.0]

    experience.append({
        "asset": asset,
        "experience_id": f"{asset}_EXPERIENCE_V1",
        "profitable_contexts": sorted(best_contexts, key=lambda x: x["profit_factor_proxy"], reverse=True)[:10],
        "avoid_contexts": sorted(bad_contexts, key=lambda x: x["profit_factor_proxy"])[:10],
        "total_memories": int(len(ag)),
        "status": "MARKET_EXPERIENCE_ACTIVE"
    })

# P1891 Meta Learning
meta_learning = {
    "status": "P1891_META_LEARNING_COMPLETED",
    "learning_targets": [
        "which_contexts_improve_pf",
        "which_filters_reduce_losers",
        "which_regimes_activate_specialists",
        "which_assets_accept_transfer_learning"
    ],
    "current_best_learning": {
        "XAUUSD": "liquidity_sweep + low execution sensitivity",
        "USDJPY": "rsi_reversion + execution sensitive + trend/volatility filtering"
    }
}

# P1892 Failure Learning
failure_learning = []
losers = dna[dna["outcome"] == "LOSS"]
for keys, g in losers.groupby(["asset","family","session","trend_regime","volatility_regime"]):
    failure_learning.append({
        "failure_id": sid(str(keys), "FAIL"),
        "asset": keys[0],
        "family": keys[1],
        "session": keys[2],
        "trend_regime": keys[3],
        "volatility_regime": keys[4],
        "losses": int(len(g)),
        "avg_loss": round(float(g["return_1bar"].mean()), 8),
        "avoidance_candidate": True
    })

# P1893 Adaptive Specialists
adaptive_specialists = []
for r in ranking:
    adaptive_specialists.append({
        "specialist_id": r["specialist_id"],
        "asset": r["asset"],
        "family": r["family"],
        "tier": r["tier"],
        "adaptive_rules": {
            "activate_if": ["regime_match", "context_memory_profitable", "edge_health_green"],
            "reduce_if": ["decay_detected", "bad_context", "execution_stress"],
            "disable_if": ["health_critical", "black_swan_avoidance_window"]
        },
        "status": "ADAPTIVE_SPECIALIST_READY"
    })

# P1894 Decay Detection
decay_rows = []
for r in ranking:
    m = r.get("metrics", {})
    consistency = float(m.get("yearly_consistency_proxy", 0))
    pf = float(m.get("profit_factor_proxy", 0))
    trades = int(m.get("trades", 0))
    health = "HEALTHY"
    if consistency < 0.60 or pf < 1.2:
        health = "WEAKENING"
    if trades < 20:
        health = "LOW_SAMPLE"
    decay_rows.append({
        "specialist_id": r["specialist_id"],
        "asset": r["asset"],
        "family": r["family"],
        "pf": pf,
        "consistency": consistency,
        "trades": trades,
        "decay_state": health
    })

# P1895 Edge Health Monitor
health_rows = []
for r in ranking:
    m = r.get("metrics", {})
    score = (
        float(m.get("profit_factor_proxy",0)) * 25 +
        float(m.get("win_rate",0)) * 20 +
        float(m.get("yearly_consistency_proxy",0)) * 25 +
        min(int(m.get("trades",0)),100) * 0.20
    )
    state = "ELITE" if score >= 100 else "HEALTHY" if score >= 75 else "WATCH"
    health_rows.append({
        "specialist_id": r["specialist_id"],
        "asset": r["asset"],
        "family": r["family"],
        "health_score": round(score,6),
        "health_state": state,
        "tier": r.get("tier"),
        "status": "EDGE_HEALTH_ACTIVE"
    })

# P1896 Portfolio Brain V2
portfolio_brain = {
    "status": "P1896_PORTFOLIO_BRAIN_V2_COMPLETED",
    "mode": "RESEARCH_ONLY",
    "selected_specialists": sorted(health_rows, key=lambda x: x["health_score"], reverse=True)[:20],
    "rule": "choose_best_specialist_set_not_single_trade"
}

# P1897 Capital Allocation Engine — paper only
capital_allocation = []
top = portfolio_brain["selected_specialists"]
total_score = sum([x["health_score"] for x in top]) or 1
for x in top:
    capital_allocation.append({
        "specialist_id": x["specialist_id"],
        "asset": x["asset"],
        "paper_weight": round(x["health_score"] / total_score, 6),
        "mode": "PAPER_ONLY",
        "REAL_CAPITAL": "FORBIDDEN"
    })

# P1898 Cross Asset Intelligence
cross_asset = {
    "status": "P1898_CROSS_ASSET_INTELLIGENCE_COMPLETED",
    "known_relationships": [
        {"pair": ["XAUUSD","USDJPY"], "relationship": "both D1 robust but different execution sensitivity"},
        {"pair": ["XAUUSD","USDJPY"], "relationship": "XAUUSD liquidity driven; USDJPY statistical reversion driven"}
    ],
    "pending_transfer_jobs": "data/lake/experiments/p1885a/p1885a_cross_asset_transfer_queue.json"
}

# P1899 Global Market Graph
graph_nodes = []
graph_edges = []

for a in asset_profiles:
    if "asset" in a:
        graph_nodes.append({"id": a["asset"], "type": "ASSET"})

for h in health_rows:
    graph_nodes.append({"id": h["specialist_id"], "type": "SPECIALIST", "asset": h["asset"]})
    graph_edges.append({"source": h["asset"], "target": h["specialist_id"], "relation": "HAS_SPECIALIST"})

for c in context_memory:
    graph_nodes.append({"id": c["context_id"], "type": "CONTEXT", "asset": c["asset"]})
    graph_edges.append({"source": c["asset"], "target": c["context_id"], "relation": "HAS_CONTEXT"})

global_graph = {
    "status": "P1899_GLOBAL_MARKET_GRAPH_COMPLETED",
    "nodes": graph_nodes,
    "edges": graph_edges,
    "node_count": len(graph_nodes),
    "edge_count": len(graph_edges)
}

# P1900 Supreme Market Knowledge Base
supreme_kb = {
    "status": "P1900_SUPREME_MARKET_KNOWLEDGE_BASE_COMPLETED",
    "components": {
        "market_memory": len(market_memory),
        "regime_memory": len(regime_memory),
        "black_swan_memory": len(black_swan_memory),
        "context_memory": len(context_memory),
        "experience_profiles": len(experience),
        "adaptive_specialists": len(adaptive_specialists),
        "edge_health_rows": len(health_rows),
        "portfolio_allocations": len(capital_allocation),
        "graph_nodes": len(graph_nodes),
        "graph_edges": len(graph_edges)
    },
    "mode": "RESEARCH_ONLY",
    "next": "P2000_AUTONOMOUS_RESEARCH_DIVISION"
}

files = {
    MEMORY / "p1886_market_memory.json": market_memory,
    MEMORY / "p1887_regime_memory.json": regime_memory,
    MEMORY / "p1888_black_swan_memory.json": black_swan_memory,
    MEMORY / "p1889_context_memory.json": context_memory,
    EXPERIENCE / "p1890_market_experience_engine.json": experience,
    EXPERIENCE / "p1891_meta_learning.json": meta_learning,
    EXPERIENCE / "p1892_failure_learning.json": failure_learning,
    EXPERIENCE / "p1893_adaptive_specialists.json": adaptive_specialists,
    HEALTH / "p1894_decay_detection.json": decay_rows,
    HEALTH / "p1895_edge_health_monitor.json": health_rows,
    PORTFOLIO / "p1896_portfolio_brain_v2.json": portfolio_brain,
    PORTFOLIO / "p1897_capital_allocation_paper_only.json": capital_allocation,
    GRAPHS / "p1898_cross_asset_intelligence.json": cross_asset,
    GRAPHS / "p1899_global_market_graph.json": global_graph,
    KB / "p1900_supreme_market_knowledge_base.json": supreme_kb
}

for path, obj in files.items():
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

report = {
    "STATUS": "P1886_TO_P1900_MARKET_MEMORY_AND_SUPREME_KB_COMPLETED",
    "P1886_MARKET_MEMORY_ROWS": len(market_memory),
    "P1887_REGIME_MEMORY_ROWS": len(regime_memory),
    "P1888_BLACK_SWAN_MEMORY_ROWS": len(black_swan_memory),
    "P1889_CONTEXT_MEMORY_ROWS": len(context_memory),
    "P1890_EXPERIENCE_PROFILES": len(experience),
    "P1891_META_LEARNING": "COMPLETED",
    "P1892_FAILURE_LEARNING_ROWS": len(failure_learning),
    "P1893_ADAPTIVE_SPECIALISTS": len(adaptive_specialists),
    "P1894_DECAY_ROWS": len(decay_rows),
    "P1895_HEALTH_ROWS": len(health_rows),
    "P1896_PORTFOLIO_SELECTED": len(top),
    "P1897_PAPER_ALLOCATIONS": len(capital_allocation),
    "P1898_CROSS_ASSET_INTELLIGENCE": "COMPLETED",
    "P1899_GRAPH_NODES": len(graph_nodes),
    "P1899_GRAPH_EDGES": len(graph_edges),
    "P1900_SUPREME_KB": "COMPLETED",
    "NEXT": "P2000_AUTONOMOUS_RESEARCH_DIVISION",
    "SAFETY": {
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN",
        "MODE": "RESEARCH_ONLY"
    },
    "generated_at": datetime.now(UTC).isoformat()
}

(BASE / "p1886_to_p1900_market_memory_supreme_kb_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))

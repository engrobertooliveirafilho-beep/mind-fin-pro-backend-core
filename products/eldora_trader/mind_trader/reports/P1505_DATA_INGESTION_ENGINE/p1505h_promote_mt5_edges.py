import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("reports/P1505_DATA_INGESTION_ENGINE")
SRC = OUT / "p1505g_mt5_monte_carlo_results.json"
POOL = OUT / "p1505h_mt5_promoted_edge_pool.json"
REPORT = OUT / "p1505h_promote_mt5_edges_report.json"

def load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

def sig(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, default=str).encode()).hexdigest()[:24]

rows = load(SRC)
promoted = [r for r in rows if r.get("promoted_edge") is True]

pool = []
for r in promoted:
    edge = {
        "edge_id": sig([r.get("dataset"), r.get("family"), r.get("params"), "MT5_PROMOTED"]),
        "source": "MT5",
        "asset": r.get("asset"),
        "timeframe": r.get("timeframe"),
        "family": r.get("family"),
        "params": r.get("params"),
        "trades": r.get("trades"),
        "profit_factor": r.get("profit_factor"),
        "max_drawdown_proxy": r.get("max_drawdown_proxy"),
        "score": r.get("score"),
        "walk_forward_stability": r.get("walk_forward_stability"),
        "monte_carlo_survival": r.get("monte_carlo_survival"),
        "promotion_status": "PROMOTED_MT5_EDGE",
        "execution_mode": "RESEARCH_ONLY",
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN",
        "promoted_at": datetime.now(UTC).isoformat()
    }
    pool.append(edge)

POOL.write_text(json.dumps(pool, indent=2, ensure_ascii=False), encoding="utf-8")

report = {
    "STATUS": "P1505H_PROMOTE_MT5_EDGES_TO_EDGE_POOL_COMPLETED",
    "INPUT_MONTE_CARLO_ROWS": len(rows),
    "PROMOTED_MT5_EDGES": len(pool),
    "POOL_FILE": str(POOL),
    "NEXT": "P1505I_MERGE_MT5_EDGES_WITH_GLOBAL_EDGE_POOL",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))

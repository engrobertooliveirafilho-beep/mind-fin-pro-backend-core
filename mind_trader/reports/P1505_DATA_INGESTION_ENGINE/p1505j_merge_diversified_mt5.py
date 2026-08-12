import json
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("reports/P1505_DATA_INGESTION_ENGINE")
MT5_SEL = OUT / "p1505i_diversified_mt5_edge_selection.json"
GLOBAL_OUT = OUT / "p1505j_global_edge_pool_merged.json"
REPORT = OUT / "p1505j_merge_diversified_mt5_report.json"

SOURCES = [
    Path("reports/P401H_TIMEFRAME_DIVERSIFICATION_FIX/p401h_top10_timeframe_balanced.json"),
    MT5_SEL
]

def load(p):
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def key(e):
    return "|".join([
        str(e.get("asset")),
        str(e.get("timeframe") or e.get("target_timeframe")),
        str(e.get("family")),
        json.dumps(e.get("params"), sort_keys=True, default=str)
    ])

merged = []
seen = set()
input_counts = {}
duplicates = 0

 for_src = []
for src in SOURCES:
    rows = load(src)
    input_counts[str(src)] = len(rows)
    for e in rows:
        k = key(e)
        if k in seen:
            duplicates += 1
            continue
        seen.add(k)
        e["global_pool_status"] = "ACTIVE_RESEARCH_ONLY"
        e["ORDER_SENT"] = False
        e["REAL_ORDERS"] = "FORBIDDEN"
        e["FTMO_REAL"] = "FORBIDDEN"
        e["MT5_REAL"] = "FORBIDDEN"
        e["merged_at"] = datetime.now(UTC).isoformat()
        merged.append(e)

GLOBAL_OUT.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")

report = {
    "STATUS": "P1505J_MERGE_DIVERSIFIED_MT5_EDGES_WITH_GLOBAL_POOL_COMPLETED",
    "INPUT_COUNTS": input_counts,
    "MERGED_EDGE_POOL": len(merged),
    "DUPLICATES_REMOVED": duplicates,
    "OUTPUT": str(GLOBAL_OUT),
    "NEXT": "P1505K_RESELECT_TOP10_FROM_GLOBAL_POOL",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))

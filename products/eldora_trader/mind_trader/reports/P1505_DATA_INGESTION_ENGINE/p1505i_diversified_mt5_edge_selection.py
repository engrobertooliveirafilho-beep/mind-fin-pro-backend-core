import json
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("reports/P1505_DATA_INGESTION_ENGINE")
SRC = OUT / "p1505h_mt5_promoted_edge_pool.json"
SEL = OUT / "p1505i_diversified_mt5_edge_selection.json"
REPORT = OUT / "p1505i_diversified_selection_report.json"

MAX_PER_ASSET = 15
MAX_PER_TIMEFRAME = 8
MAX_PER_FAMILY = 15

def load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

pool = load(SRC)

pool = sorted(
    pool,
    key=lambda x: (
        float(x.get("score") or 0),
        float(x.get("monte_carlo_survival") or 0),
        float(x.get("profit_factor") or 0)
    ),
    reverse=True
)

asset_count = {}
tf_count = {}
family_count = {}

selected = []
rejected = []

for e in pool:
    asset = e.get("asset")
    tf = e.get("timeframe")
    fam = e.get("family")

    if asset_count.get(asset, 0) >= MAX_PER_ASSET:
        e["rejection_reason"] = "ASSET_CAP"
        rejected.append(e)
        continue

    if tf_count.get(tf, 0) >= MAX_PER_TIMEFRAME:
        e["rejection_reason"] = "TIMEFRAME_CAP"
        rejected.append(e)
        continue

    if family_count.get(fam, 0) >= MAX_PER_FAMILY:
        e["rejection_reason"] = "FAMILY_CAP"
        rejected.append(e)
        continue

    e["diversified_selection_status"] = "SELECTED"
    e["execution_mode"] = "RESEARCH_ONLY"
    e["ORDER_SENT"] = False
    e["REAL_ORDERS"] = "FORBIDDEN"
    e["FTMO_REAL"] = "FORBIDDEN"
    e["MT5_REAL"] = "FORBIDDEN"
    selected.append(e)

    asset_count[asset] = asset_count.get(asset, 0) + 1
    tf_count[tf] = tf_count.get(tf, 0) + 1
    family_count[fam] = family_count.get(fam, 0) + 1

SEL.write_text(json.dumps(selected, indent=2, ensure_ascii=False), encoding="utf-8")

report = {
    "STATUS": "P1505I_DIVERSIFIED_MT5_EDGE_SELECTION_COMPLETED",
    "INPUT_EDGES": len(pool),
    "SELECTED_EDGES": len(selected),
    "REJECTED_EDGES": len(rejected),
    "MAX_PER_ASSET": MAX_PER_ASSET,
    "MAX_PER_TIMEFRAME": MAX_PER_TIMEFRAME,
    "MAX_PER_FAMILY": MAX_PER_FAMILY,
    "ASSET_DISTRIBUTION": asset_count,
    "TIMEFRAME_DISTRIBUTION": tf_count,
    "FAMILY_DISTRIBUTION": family_count,
    "OUTPUT": str(SEL),
    "NEXT": "P1505J_MERGE_DIVERSIFIED_MT5_EDGES_WITH_GLOBAL_POOL",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))

import json
import pandas as pd
from pathlib import Path
from datetime import datetime, UTC

QUEUE = Path("data/harvest_queue/global_harvest_queue.json")
DATA = Path("data/normalized")
OUT = Path("reports/P1802_DATA_AVAILABILITY_AUDIT")
REPORT = OUT / "p1802_data_availability_report.json"

queue = json.loads(QUEUE.read_text(encoding="utf-8"))

def parse_dataset_name(f):
    name = f.stem.replace("_normalized","")
    parts = name.split("_")

    if name.startswith("MT5_") and len(parts) >= 3:
        return parts[1], parts[2]

    tf_list = ["M1","M5","M15","M20","M30","H1","H4","D1","W1","MN1"]
    tf = parts[-1] if parts[-1] in tf_list else "UNKNOWN"
    asset = "_".join(parts[:-1]) if tf != "UNKNOWN" else name
    return asset, tf

def parse_time(df):
    lower = {c.lower(): c for c in df.columns}
    col = lower.get("time") or lower.get("datetime") or lower.get("date") or lower.get("timestamp") or lower.get("data")
    if not col:
        return None
    s = df[col].astype(str)
    sample = s.dropna().astype(str).head(20).to_list()
    dayfirst = any("/" in x and len(x.split("/")[0]) <= 2 for x in sample)
    return pd.to_datetime(s, errors="coerce", dayfirst=dayfirst)

available = {}

for f in DATA.glob("*.csv"):
    try:
        asset, tf = parse_dataset_name(f)
        df = pd.read_csv(f)
        t = parse_time(df)

        if t is None:
            available[(asset, tf)] = {
                "dataset": str(f),
                "available": False,
                "reason": "NO_TIME_COLUMN"
            }
            continue

        t = t.dropna()
        if t.empty:
            available[(asset, tf)] = {
                "dataset": str(f),
                "available": False,
                "reason": "EMPTY_TIME"
            }
            continue

        start = t.min()
        end = t.max()
        years = (end - start).days / 365 if end > start else 0

        available[(asset, tf)] = {
            "dataset": str(f),
            "available": True,
            "rows": len(df),
            "start": str(start),
            "end": str(end),
            "history_years": round(years, 4)
        }

    except Exception as e:
        available[(f.stem, "UNKNOWN")] = {
            "dataset": str(f),
            "available": False,
            "reason": str(e)
        }

audit = []
missing = []
sufficient = []

for q in queue:
    key = (q["asset"], q["timeframe"])
    have = available.get(key)
    required = float(q["history_years_target"])

    row = {
        "asset": q["asset"],
        "market": q["market"],
        "timeframe": q["timeframe"],
        "priority": q["priority"],
        "required_years": required,
        "status": "MISSING_DATA",
        "available_years": 0,
        "gap_years": required
    }

    if have and have.get("available"):
        years = float(have.get("history_years") or 0)
        row.update({
            "status": "SUFFICIENT" if years >= required else "INSUFFICIENT_HISTORY",
            "available_years": years,
            "gap_years": round(max(required - years, 0), 4),
            "dataset": have.get("dataset"),
            "rows": have.get("rows"),
            "start": have.get("start"),
            "end": have.get("end")
        })

    audit.append(row)

    if row["status"] == "SUFFICIENT":
        sufficient.append(row)
    else:
        missing.append(row)

missing_sorted = sorted(missing, key=lambda x: (x["priority"], x["gap_years"]), reverse=True)

report = {
    "STATUS": "P1802_DATA_AVAILABILITY_AUDIT_COMPLETED",
    "QUEUE_ITEMS": len(queue),
    "DATASETS_AVAILABLE_KEYS": len(available),
    "SUFFICIENT": len(sufficient),
    "MISSING_OR_INSUFFICIENT": len(missing),
    "P5_MISSING_OR_INSUFFICIENT": len([x for x in missing if x["priority"] == 5]),
    "TOP50_GAPS": missing_sorted[:50],
    "NEXT": "P1803_PRIORITY_HARVEST_PLAN_AND_BACKTEST_UNLOCK",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(OUT/"p1802_data_availability_detail.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT/"p1802_missing_history_queue.json").write_text(json.dumps(missing_sorted, indent=2, ensure_ascii=False), encoding="utf-8")
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(report, indent=2, ensure_ascii=False))

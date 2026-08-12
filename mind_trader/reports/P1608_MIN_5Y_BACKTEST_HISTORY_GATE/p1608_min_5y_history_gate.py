import json
import pandas as pd
from pathlib import Path
from datetime import datetime, UTC

DATA = Path("data/normalized")
OUT = Path("reports/P1608_MIN_5Y_BACKTEST_HISTORY_GATE")
REPORT = OUT / "p1608_min_5y_history_gate_report.json"
OUT.mkdir(parents=True, exist_ok=True)

MIN_YEARS = 5
MIN_DAYS = 365 * MIN_YEARS

rows = []

for f in DATA.glob("*.csv"):
    try:
        df = pd.read_csv(f, usecols=["time"])
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df = df.dropna(subset=["time"])

        if df.empty:
            continue

        start = df["time"].min()
        end = df["time"].max()
        days = (end - start).days
        years = days / 365 if days > 0 else 0

        name = f.stem.replace("_normalized", "")
        parts = name.split("_")

        if name.startswith("MT5_") and len(parts) >= 3:
            asset = parts[1]
            timeframe = parts[2]
        else:
            timeframe = parts[-1] if parts[-1] in ["M1","M5","M15","M20","M30","H1","H4","D1","W1","MN1"] else "UNKNOWN"
            asset = "_".join(parts[:-1]) if timeframe != "UNKNOWN" else name

        rows.append({
            "dataset": str(f),
            "asset": asset,
            "timeframe": timeframe,
            "rows": len(df),
            "start": str(start),
            "end": str(end),
            "history_days": days,
            "history_years": round(years, 2),
            "min_5y_pass": days >= MIN_DAYS
        })

    except Exception as e:
        rows.append({
            "dataset": str(f),
            "error": str(e),
            "min_5y_pass": False
        })

passed = [r for r in rows if r.get("min_5y_pass")]
failed = [r for r in rows if not r.get("min_5y_pass")]

report = {
    "STATUS": "P1608_MIN_5Y_BACKTEST_HISTORY_GATE_COMPLETED",
    "DATASETS_AUDITED": len(rows),
    "MIN_REQUIRED_YEARS": MIN_YEARS,
    "PASSED_5Y": len(passed),
    "FAILED_5Y": len(failed),
    "PASS_RATE": round(len(passed) / max(len(rows), 1), 4),
    "PASSED_BY_ASSET": sorted(list(set(r["asset"] for r in passed if "asset" in r))),
    "FAILED_SAMPLE": failed[:30],
    "NEXT": "P1609_REHARVEST_5Y_MT5_HISTORY_AND_REBACKTEST",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(OUT / "p1608_dataset_history_detail.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(report, indent=2, ensure_ascii=False))

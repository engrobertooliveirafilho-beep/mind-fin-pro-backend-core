import json
import pandas as pd
from pathlib import Path
from datetime import datetime, UTC

RAW = Path("data/raw/mt5")
NORM = Path("data/normalized")
QUAR = Path("data/quarantine")
OUT = Path("reports/P1505_DATA_INGESTION_ENGINE")

RAW.mkdir(parents=True, exist_ok=True)
NORM.mkdir(parents=True, exist_ok=True)
QUAR.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

required = ["time","open","high","low","close","tick_volume"]

results = []
normalized = 0
quarantined = 0
rows_total = 0

for f in RAW.glob("MT5_*_*_raw.csv"):
    try:
        df = pd.read_csv(f)

        missing = [c for c in required if c not in df.columns]
        if missing:
            quarantined += 1
            results.append({
                "file": str(f),
                "status": "QUARANTINED",
                "reason": f"MISSING_COLUMNS:{missing}"
            })
            f.rename(QUAR / f.name)
            continue

        df = df[required].copy()
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df = df.dropna(subset=["time","open","high","low","close"])
        df = df.drop_duplicates(subset=["time"])
        df = df.sort_values("time")

        for col in ["open","high","low","close","tick_volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["open","high","low","close"])

        invalid_ohlc = df[
            (df["high"] < df["low"]) |
            (df["high"] < df["open"]) |
            (df["high"] < df["close"]) |
            (df["low"] > df["open"]) |
            (df["low"] > df["close"])
        ]

        if len(df) < 100:
            quarantined += 1
            results.append({
                "file": str(f),
                "status": "QUARANTINED",
                "reason": "TOO_FEW_ROWS",
                "rows": len(df)
            })
            f.rename(QUAR / f.name)
            continue

        if len(invalid_ohlc) > 0:
            quarantined += 1
            results.append({
                "file": str(f),
                "status": "QUARANTINED",
                "reason": "INVALID_OHLC",
                "invalid_rows": len(invalid_ohlc)
            })
            f.rename(QUAR / f.name)
            continue

        out_name = f.name.replace("_raw.csv", "_normalized.csv")
        out_file = NORM / out_name

        df.to_csv(out_file, index=False)

        normalized += 1
        rows_total += len(df)

        results.append({
            "file": str(f),
            "status": "NORMALIZED",
            "rows": len(df),
            "output": str(out_file)
        })

    except Exception as e:
        quarantined += 1
        results.append({
            "file": str(f),
            "status": "ERROR",
            "error": str(e)
        })

report = {
    "STATUS": "P1505C_MT5_RAW_TO_NORMALIZED_COMPLETED",
    "RAW_FILES_INPUT": len(list(RAW.glob("MT5_*_*_raw.csv"))) + quarantined,
    "NORMALIZED_FILES_CREATED": normalized,
    "QUARANTINED_FILES": quarantined,
    "ROWS_TOTAL": rows_total,
    "RESULTS": results,
    "NEXT": "P1505D_DATA_QUALITY_ENGINE",
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(OUT / "p1505c_mt5_raw_to_normalized_report.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(report, indent=2, ensure_ascii=False))

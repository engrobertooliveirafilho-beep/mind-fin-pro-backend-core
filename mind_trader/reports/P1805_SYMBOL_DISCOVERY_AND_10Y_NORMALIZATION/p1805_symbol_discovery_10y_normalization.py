import json
import pandas as pd
from pathlib import Path
from datetime import datetime, UTC

PROBE = Path("data/raw/mt5_probe")
OUT = Path("reports/P1805_SYMBOL_DISCOVERY_AND_10Y_NORMALIZATION")
NORM = Path("data/normalized_10y")
REPORT = OUT / "p1805_symbol_discovery_10y_normalization_report.json"

normalized = []
errors = []

for f in PROBE.glob("MT5_PROBE_*.csv"):
    try:
        name = f.stem.replace("MT5_PROBE_", "")
        parts = name.split("_")
        asset = parts[0]
        timeframe = parts[1]

        df = pd.read_csv(f)

        rename = {
            "time": "time",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "tick_volume": "volume"
        }

        df = df.rename(columns=rename)
        keep = [c for c in ["time","open","high","low","close","volume"] if c in df.columns]
        df = df[keep].copy()

        df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
        for c in ["open","high","low","close","volume"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")

        df = df.dropna(subset=["time","open","high","low","close"])
        df = df.drop_duplicates(subset=["time"]).sort_values("time").reset_index(drop=True)

        years = (df["time"].max() - df["time"].min()).days / 365 if len(df) else 0

        out_file = NORM / f"MT5_{asset}_{timeframe}_10Y_normalized.csv"
        df.to_csv(out_file, index=False)

        normalized.append({
            "asset": asset,
            "timeframe": timeframe,
            "rows": int(len(df)),
            "start": str(df["time"].min()),
            "end": str(df["time"].max()),
            "history_years": round(years, 4),
            "meets_10y": years >= 10,
            "file": str(out_file),
            "status": "NORMALIZED_10Y"
        })

    except Exception as e:
        errors.append({
            "file": str(f),
            "error": str(e)
        })

symbol_discovery = []

try:
    import MetaTrader5 as mt5
    if mt5.initialize():
        symbols = mt5.symbols_get()
        names = [s.name for s in symbols] if symbols else []

        targets = ["BTC", "NAS", "US100", "USTEC", "NDX", "NASDAQ", "CRYPTO", "BITCOIN"]
        for n in names:
            upper = n.upper()
            if any(t in upper for t in targets):
                symbol_discovery.append(n)

        mt5.shutdown()
except Exception as e:
    errors.append({
        "stage": "SYMBOL_DISCOVERY",
        "error": str(e)
    })

report = {
    "STATUS": "P1805_SYMBOL_DISCOVERY_AND_10Y_NORMALIZATION_COMPLETED",
    "NORMALIZED_10Y_FILES": len(normalized),
    "MEETS_10Y": len([x for x in normalized if x["meets_10y"]]),
    "SYMBOL_DISCOVERY_CANDIDATES_FOR_BTC_NAS100": sorted(symbol_discovery)[:200],
    "ERRORS": errors,
    "NEXT": "P1806_BACKTEST_UNLOCK_FOR_10Y_NORMALIZED_DATA",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(OUT / "p1805_normalized_10y_detail.json").write_text(json.dumps(normalized, indent=2, ensure_ascii=False), encoding="utf-8")
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(report, indent=2, ensure_ascii=False))

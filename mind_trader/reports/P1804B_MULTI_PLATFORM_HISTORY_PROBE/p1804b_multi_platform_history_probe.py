import json
import pandas as pd
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("reports/P1804B_MULTI_PLATFORM_HISTORY_PROBE")
RAW = Path("data/raw/platform_probe")
REPORT = OUT / "p1804b_multi_platform_history_probe_report.json"

platforms = {
    "MT5": {
        "path": Path("data/raw/platform_probe/mt5"),
        "status": "CHECK_BY_API_OR_EXPORTED_CSV"
    },
    "PROFIT_NELOGICA": {
        "path": Path("data/raw/platform_probe/profit"),
        "status": "CHECK_EXPORTED_CSV"
    },
    "BLACKARROW_ACTIVETRADER": {
        "path": Path("data/raw/platform_probe/blackarrow"),
        "status": "CHECK_EXPORTED_CSV"
    }
}

priority_assets = ["XAUUSD","USDJPY","GBPUSD","EURUSD","USDCAD","BTCUSD","NAS100","WINFUT","WDOFUT"]
timeframes = ["M5","M15","M30","H1","H4","D1"]

def detect_time_col(df):
    lower = {c.lower().strip(): c for c in df.columns}
    return (
        lower.get("time") or
        lower.get("datetime") or
        lower.get("date") or
        lower.get("data") or
        lower.get("timestamp") or
        lower.get("dt") or
        lower.get("date_time")
    )

def detect_ohlc(df):
    lower = {c.lower().strip(): c for c in df.columns}
    return {
        "open": lower.get("open") or lower.get("abertura") or lower.get("o"),
        "high": lower.get("high") or lower.get("maxima") or lower.get("máxima") or lower.get("h"),
        "low": lower.get("low") or lower.get("minima") or lower.get("mínima") or lower.get("l"),
        "close": lower.get("close") or lower.get("fechamento") or lower.get("c") or lower.get("ultimo") or lower.get("último")
    }

def parse_time(series):
    sample = series.dropna().astype(str).head(30).to_list()
    dayfirst = any("/" in x for x in sample)
    return pd.to_datetime(series, errors="coerce", dayfirst=dayfirst)

def infer_asset_tf(filename):
    name = filename.upper().replace(".CSV","")
    found_asset = None
    found_tf = None

    for a in priority_assets:
        if a.upper() in name:
            found_asset = a
            break

    for tf in timeframes:
        if f"_{tf}" in name or f"-{tf}" in name or name.endswith(tf):
            found_tf = tf
            break

    return found_asset or "UNKNOWN", found_tf or "UNKNOWN"

results = []

for platform, meta in platforms.items():
    p = meta["path"]
    files = list(p.glob("*.csv"))

    if not files:
        results.append({
            "platform": platform,
            "status": "NO_CSV_FILES_FOUND",
            "path": str(p),
            "instruction": "Exportar CSV histórico da plataforma para esta pasta e rodar novamente."
        })
        continue

    for f in files:
        try:
            df = pd.read_csv(f, sep=None, engine="python")
            time_col = detect_time_col(df)
            ohlc = detect_ohlc(df)
            asset, tf = infer_asset_tf(f.name)

            if not time_col:
                results.append({
                    "platform": platform,
                    "file": str(f),
                    "asset": asset,
                    "timeframe": tf,
                    "status": "FAILED_NO_TIME_COLUMN",
                    "columns": list(df.columns)
                })
                continue

            missing_ohlc = [k for k,v in ohlc.items() if not v]
            if missing_ohlc:
                results.append({
                    "platform": platform,
                    "file": str(f),
                    "asset": asset,
                    "timeframe": tf,
                    "status": "FAILED_MISSING_OHLC",
                    "missing": missing_ohlc,
                    "columns": list(df.columns)
                })
                continue

            t = parse_time(df[time_col]).dropna()
            if t.empty:
                results.append({
                    "platform": platform,
                    "file": str(f),
                    "asset": asset,
                    "timeframe": tf,
                    "status": "FAILED_TIME_PARSE_EMPTY",
                    "time_col": time_col
                })
                continue

            years = (t.max() - t.min()).days / 365 if t.max() > t.min() else 0

            results.append({
                "platform": platform,
                "file": str(f),
                "asset": asset,
                "timeframe": tf,
                "status": "CSV_AUDITED",
                "rows": int(len(df)),
                "start": str(t.min()),
                "end": str(t.max()),
                "history_years": round(years, 4),
                "meets_10y": years >= 10,
                "meets_5y": years >= 5,
                "time_column": time_col,
                "ohlc_columns": ohlc
            })

        except Exception as e:
            results.append({
                "platform": platform,
                "file": str(f),
                "status": "ERROR",
                "error": str(e)
            })

platform_summary = {}
for platform in platforms:
    rows = [r for r in results if r["platform"] == platform]
    platform_summary[platform] = {
        "files_checked": len([r for r in rows if "file" in r]),
        "csv_audited": len([r for r in rows if r.get("status") == "CSV_AUDITED"]),
        "meets_10y": len([r for r in rows if r.get("meets_10y")]),
        "meets_5y": len([r for r in rows if r.get("meets_5y")]),
        "no_files": len([r for r in rows if r.get("status") == "NO_CSV_FILES_FOUND"])
    }

report = {
    "STATUS": "P1804B_MULTI_PLATFORM_HISTORY_PROBE_COMPLETED",
    "OBJECTIVE": "Testar capacidade real de histórico por MT5, Profit/Nelogica e BlackArrow ActiveTrader via API/CSV",
    "PLATFORM_SUMMARY": platform_summary,
    "RESULTS": results,
    "EXPORT_FOLDERS": {
        "MT5": "data/raw/platform_probe/mt5",
        "PROFIT_NELOGICA": "data/raw/platform_probe/profit",
        "BLACKARROW_ACTIVETRADER": "data/raw/platform_probe/blackarrow"
    },
    "NEXT": "EXPORT_REAL_CSV_FROM_PROFIT_AND_BLACKARROW_THEN_RERUN_PROBE",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(OUT / "p1804b_multi_platform_history_probe_detail.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))

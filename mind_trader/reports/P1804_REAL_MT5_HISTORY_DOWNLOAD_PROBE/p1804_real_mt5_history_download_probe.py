import json
from pathlib import Path
from datetime import datetime, UTC, timedelta

OUT = Path("reports/P1804_REAL_MT5_HISTORY_DOWNLOAD_PROBE")
RAW = Path("data/raw/mt5_probe")
REPORT = OUT / "p1804_real_mt5_history_download_probe_report.json"

symbols = ["XAUUSD","USDJPY","GBPUSD","EURUSD","USDCAD","BTCUSD","NAS100"]
timeframes = ["D1","H4","H1"]

mt5_available = False
mt5_error = None
results = []

try:
    import MetaTrader5 as mt5
    mt5_available = True
except Exception as e:
    mt5_error = str(e)

tf_map = {}

if mt5_available:
    try:
        tf_map = {
            "D1": mt5.TIMEFRAME_D1,
            "H4": mt5.TIMEFRAME_H4,
            "H1": mt5.TIMEFRAME_H1
        }

        initialized = mt5.initialize()

        if not initialized:
            mt5_error = str(mt5.last_error())
        else:
            start = datetime.now(UTC) - timedelta(days=365*11)
            end = datetime.now(UTC)

            for sym in symbols:
                for tf_name, tf_const in tf_map.items():
                    try:
                        rates = mt5.copy_rates_range(sym, tf_const, start, end)

                        if rates is None or len(rates) == 0:
                            results.append({
                                "symbol": sym,
                                "timeframe": tf_name,
                                "status": "NO_DATA",
                                "bars": 0,
                                "error": str(mt5.last_error())
                            })
                            continue

                        import pandas as pd
                        df = pd.DataFrame(rates)
                        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)

                        years = (df["time"].max() - df["time"].min()).days / 365

                        out_file = RAW / f"MT5_PROBE_{sym}_{tf_name}.csv"
                        df.to_csv(out_file, index=False)

                        results.append({
                            "symbol": sym,
                            "timeframe": tf_name,
                            "status": "DOWNLOADED",
                            "bars": int(len(df)),
                            "start": str(df["time"].min()),
                            "end": str(df["time"].max()),
                            "history_years": round(years, 4),
                            "meets_10y": years >= 10,
                            "meets_5y": years >= 5,
                            "file": str(out_file)
                        })

                    except Exception as e:
                        results.append({
                            "symbol": sym,
                            "timeframe": tf_name,
                            "status": "ERROR",
                            "error": str(e)
                        })

            mt5.shutdown()

    except Exception as e:
        mt5_error = str(e)

report = {
    "STATUS": "P1804_REAL_MT5_HISTORY_DOWNLOAD_PROBE_COMPLETED",
    "MT5_MODULE_AVAILABLE": mt5_available,
    "MT5_ERROR": mt5_error,
    "TESTS": len(results),
    "DOWNLOADED": len([r for r in results if r.get("status") == "DOWNLOADED"]),
    "MEETS_10Y": len([r for r in results if r.get("meets_10y")]),
    "MEETS_5Y": len([r for r in results if r.get("meets_5y")]),
    "RESULTS": results,
    "NEXT": "P1805_DECIDE_MT5_OR_CSV_FALLBACK_FOR_10Y_HISTORY",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))

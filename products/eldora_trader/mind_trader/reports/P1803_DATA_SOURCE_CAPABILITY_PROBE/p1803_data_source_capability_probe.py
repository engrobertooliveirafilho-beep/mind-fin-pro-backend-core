import json
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("reports/P1803_DATA_SOURCE_CAPABILITY_PROBE")
REPORT = OUT / "p1803_data_source_capability_probe_report.json"

priority_assets = ["XAUUSD","USDJPY","GBPUSD","EURUSD","USDCAD","BTCUSD","NAS100"]
timeframes = ["M5","M15","M30","H1","H4","D1"]

sources = [
    {
        "source": "MT5",
        "status": "NEEDS_PROBE",
        "test_method": "export/request max bars per symbol/timeframe",
        "expected_strength": "Forex/metals/index if broker provides history",
        "risk": "broker may limit candles"
    },
    {
        "source": "Nelogica/Profit",
        "status": "NEEDS_PROBE",
        "test_method": "export historical bars by asset/timeframe",
        "expected_strength": "Brazilian assets/futures",
        "risk": "export limits and subscription limits"
    },
    {
        "source": "CSV_IMPORT",
        "status": "READY",
        "test_method": "manual import from external provider",
        "expected_strength": "universal fallback",
        "risk": "data quality and timezone normalization"
    }
]

probe_matrix = []

for asset in priority_assets:
    for tf in timeframes:
        probe_matrix.append({
            "asset": asset,
            "timeframe": tf,
            "target_years": 10,
            "minimum_acceptable_years": 5,
            "preferred_sources": ["MT5","CSV_IMPORT"] if asset not in ["WINFUT","WDOFUT"] else ["Nelogica/Profit","CSV_IMPORT"],
            "probe_status": "PENDING_REAL_DOWNLOAD_TEST",
            "success_criteria": {
                "history_years": ">=10 preferred / >=5 acceptable",
                "ohlc_columns": "open,high,low,close",
                "time_column": "required",
                "duplicates": "0 or removable",
                "timezone": "normalized",
                "rows": "sufficient for timeframe"
            }
        })

report = {
    "STATUS": "P1803_DATA_SOURCE_CAPABILITY_PROBE_CREATED",
    "OBJECTIVE": "Prove whether the environment can access 10 years of market history",
    "PRIORITY_ASSETS": priority_assets,
    "TIMEFRAMES": timeframes,
    "PROBE_TESTS": len(probe_matrix),
    "SOURCES": sources,
    "NEXT": "RUN_REAL_MT5_EXPORT_TEST_FOR_PRIORITY_ASSETS",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(OUT/"p1803_probe_matrix.json").write_text(json.dumps(probe_matrix, indent=2, ensure_ascii=False), encoding="utf-8")
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(report, indent=2, ensure_ascii=False))

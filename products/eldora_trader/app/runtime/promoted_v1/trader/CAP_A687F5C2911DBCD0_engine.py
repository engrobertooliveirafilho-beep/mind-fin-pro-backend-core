import json
from pathlib import Path
from datetime import datetime, UTC

REQUIRED_DATASETS=[
 {"asset":"WIN","timeframe":"M1","period":"2024_2026","target":"data/incoming/profit/WIN_M1_2024_2026.csv","priority":"CRITICAL"},
 {"asset":"WDO","timeframe":"M1","period":"2024_2026","target":"data/incoming/profit/WDO_M1_2024_2026.csv","priority":"CRITICAL"},
 {"asset":"PETR4","timeframe":"D1","period":"2020_2026","target":"data/incoming/profit/PETR4_D1_2020_2026.csv","priority":"HIGH"},
 {"asset":"VALE3","timeframe":"D1","period":"2020_2026","target":"data/incoming/profit/VALE3_D1_2020_2026.csv","priority":"HIGH"},
 {"asset":"AAPL","timeframe":"D1","period":"2020_2026","target":"data/incoming/mt5/AAPL_D1_2020_2026.csv","priority":"HIGH"},
 {"asset":"NVDA","timeframe":"D1","period":"2020_2026","target":"data/incoming/mt5/NVDA_D1_2020_2026.csv","priority":"HIGH"},
 {"asset":"EURUSD","timeframe":"M15","period":"2022_2026","target":"data/incoming/mt5/EURUSD_M15_2022_2026.csv","priority":"HIGH"},
 {"asset":"XAUUSD","timeframe":"M15","period":"2022_2026","target":"data/incoming/mt5/XAUUSD_M15_2022_2026.csv","priority":"HIGH"},
 {"asset":"BTCUSD","timeframe":"H1","period":"2021_2026","target":"data/incoming/mt5/BTCUSD_H1_2021_2026.csv","priority":"HIGH"}
]

REQUIRED_COLUMNS=["time","open","high","low","close","volume"]

def run():
    out=Path("reports/P13.7_REAL_DATA_REQUIREMENT_PACK")
    out.mkdir(parents=True,exist_ok=True)

    for row in REQUIRED_DATASETS:
        Path(row["target"]).parent.mkdir(parents=True,exist_ok=True)

    manifest={
        "STATUS":"P13.7_REAL_DATA_REQUIREMENT_PACK_IMPLEMENTED",
        "REQUIRED_DATASETS":REQUIRED_DATASETS,
        "REQUIRED_COLUMNS":REQUIRED_COLUMNS,
        "MIN_ROWS_PER_DATASET":200,
        "FILE_NAMING_RULE":"ASSET_TIMEFRAME_PERIOD.csv",
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "NEXT":"PLACE_REAL_CSV_FILES_AND_RERUN_P13.3_TO_P13.6",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (out/"required_datasets.json").write_text(json.dumps(REQUIRED_DATASETS,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P13.7_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))

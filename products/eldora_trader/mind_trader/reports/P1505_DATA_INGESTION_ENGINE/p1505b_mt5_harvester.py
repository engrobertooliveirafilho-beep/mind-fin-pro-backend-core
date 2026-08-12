import json
from pathlib import Path
from datetime import datetime, UTC
import MetaTrader5 as mt5
import pandas as pd

OUT = Path("reports/P1505_DATA_INGESTION_ENGINE")
RAW = Path("data/raw/mt5")
OUT.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)

SYMBOLS = ["EURUSD","GBPUSD","AUDUSD","USDCAD","USDJPY","XAUUSD"]
TIMEFRAMES = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}

BARS = {
    "M1": 5000,
    "M5": 5000,
    "M15": 5000,
    "M30": 5000,
    "H1": 5000,
    "H4": 3000,
    "D1": 1500,
}

BLOCKS = {
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN"
}

def run():
    initialized = mt5.initialize()
    terminal = mt5.terminal_info() if initialized else None
    account = mt5.account_info() if initialized else None

    results = []
    files_created = 0
    bars_total = 0

    if not initialized:
        report = {
            "STATUS": "P1505B_MT5_HARVESTER_FAILED",
            "MT5_INITIALIZED": False,
            "ERROR": str(mt5.last_error()),
            **BLOCKS,
            "generated_at": datetime.now(UTC).isoformat()
        }
        (OUT/"p1505b_mt5_harvester_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        return

    for symbol in SYMBOLS:
        mt5.symbol_select(symbol, True)

        for tf_name, tf_value in TIMEFRAMES.items():
            rates = mt5.copy_rates_from_pos(symbol, tf_value, 0, BARS[tf_name])

            if rates is None or len(rates) == 0:
                results.append({
                    "symbol": symbol,
                    "timeframe": tf_name,
                    "status": "NO_DATA",
                    "rows": 0,
                    "file": None
                })
                continue

            df = pd.DataFrame(rates)
            df["time"] = pd.to_datetime(df["time"], unit="s")

            file = RAW / f"MT5_{symbol}_{tf_name}_raw.csv"
            df.to_csv(file, index=False)

            files_created += 1
            bars_total += len(df)

            results.append({
                "symbol": symbol,
                "timeframe": tf_name,
                "status": "RAW_SAVED",
                "rows": len(df),
                "file": str(file)
            })

    report = {
        "STATUS": "P1505B_MT5_HARVESTER_COMPLETED",
        "MT5_INITIALIZED": initialized,
        "ACCOUNT_LOGIN": account.login if account else None,
        "ACCOUNT_SERVER": account.server if account else None,
        "TERMINAL_CONNECTED": terminal.connected if terminal else None,
        "SYMBOLS": len(SYMBOLS),
        "TIMEFRAMES": len(TIMEFRAMES),
        "FILES_CREATED": files_created,
        "BARS_TOTAL": bars_total,
        "RESULTS": results,
        "NEXT": "P1505C_MT5_RAW_TO_NORMALIZED",
        **BLOCKS,
        "generated_at": datetime.now(UTC).isoformat()
    }

    (OUT/"p1505b_mt5_harvester_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()

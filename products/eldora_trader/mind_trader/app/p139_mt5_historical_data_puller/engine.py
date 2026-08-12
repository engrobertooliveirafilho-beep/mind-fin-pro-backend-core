import json, csv, hashlib
from pathlib import Path
from datetime import datetime, UTC

MT5_PATH=r"C:\Program Files\MetaTrader 5\terminal64.exe"

SYMBOLS=["EURUSD","GBPUSD","USDJPY","AUDUSD","USDCAD","XAUUSD","BTCUSD","ETHUSD"]
TIMEFRAMES={"M1":"TIMEFRAME_M1","M5":"TIMEFRAME_M5","M15":"TIMEFRAME_M15","M30":"TIMEFRAME_M30","H1":"TIMEFRAME_H1","H4":"TIMEFRAME_H4","D1":"TIMEFRAME_D1"}

def dataset_id(symbol,timeframe,rows):
    return hashlib.sha256(f"MT5:{symbol}:{timeframe}:{rows}".encode()).hexdigest()[:18]

def normalize_rates(rates):
    out=[]
    if rates is None:
        return out
    for r in rates:
        out.append({
            "time":datetime.fromtimestamp(int(r["time"]), UTC).isoformat(),
            "open":float(r["open"]),
            "high":float(r["high"]),
            "low":float(r["low"]),
            "close":float(r["close"]),
            "tick_volume":int(r["tick_volume"]),
            "spread":int(r["spread"]),
            "real_volume":int(r["real_volume"])
        })
    return out

def write_csv(path, rows):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    cols=["time","open","high","low","close","tick_volume","spread","real_volume"]
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

def pull(count=500):
    report={"connected":False,"datasets":[],"errors":[]}
    try:
        import MetaTrader5 as mt5
        ok=mt5.initialize(path=MT5_PATH)
        report["connected"]=bool(ok)
        report["last_error"]=mt5.last_error()
        if not ok:
            return report

        for symbol in SYMBOLS:
            mt5.symbol_select(symbol, True)
            for tf_name, tf_attr in TIMEFRAMES.items():
                tf=getattr(mt5,tf_attr)
                rates=mt5.copy_rates_from_pos(symbol,tf,0,count)
                rows=normalize_rates(rates)
                if not rows:
                    report["errors"].append({"symbol":symbol,"timeframe":tf_name,"error":"NO_RATES"})
                    continue
                out=f"data/normalized/MT5_{symbol}_{tf_name}.csv"
                write_csv(out,rows)
                report["datasets"].append({
                    "dataset_id":dataset_id(symbol,tf_name,len(rows)),
                    "source":"MT5",
                    "symbol":symbol,
                    "timeframe":tf_name,
                    "rows":len(rows),
                    "path":out,
                    "certification_required":True,
                    "live":"FORBIDDEN",
                    "real_broker":"DISABLED"
                })
        mt5.shutdown()
    except Exception as e:
        report["errors"].append({"error":str(e)})
    return report

def run():
    out=Path("reports/P13.9_MT5_HISTORICAL_DATA_PULLER")
    out.mkdir(parents=True,exist_ok=True)
    report=pull()
    manifest={
        "STATUS":"P13.9_MT5_HISTORICAL_DATA_PULLER_IMPLEMENTED",
        "MT5_CONNECTED":report["connected"],
        "DATASETS_CREATED":len(report["datasets"]),
        "ERRORS":report["errors"],
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"P13.9_pull_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P13.9_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))

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
    # A general helper; invoking it is not a certified MT5 data pull.
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    cols=["time","open","high","low","close","tick_volume","spread","real_volume"]
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

def pull(count=500):
    raise PermissionError("ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED")

def run():
    # Never create report folders before the MT5 admission gate.
    return pull()

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))

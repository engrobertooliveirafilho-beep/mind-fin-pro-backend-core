import json, csv
from pathlib import Path
from datetime import datetime, UTC

def mt5_probe():
    try:
        import MetaTrader5 as mt5
    except Exception as e:
        return {"platform":"MT5","available":False,"reason":"MetaTrader5 python package not installed","error":str(e)}
    try:
        ok=mt5.initialize()
        info=mt5.terminal_info() if ok else None
        mt5.shutdown()
        return {"platform":"MT5","available":bool(ok),"terminal_info":str(info),"reason":None if ok else "mt5.initialize failed"}
    except Exception as e:
        return {"platform":"MT5","available":False,"reason":"MT5 terminal connection failed","error":str(e)}

def profit_probe(path="data/incoming/profit"):
    p=Path(path); p.mkdir(parents=True,exist_ok=True)
    files=list(p.glob("*.csv"))
    return {"platform":"PROFIT","available":len(files)>0,"mode":"LOCAL_EXPORT_BRIDGE","watch_dir":str(p),"csv_files":len(files)}

def ftmo_probe(path="data/incoming/ftmo"):
    p=Path(path); p.mkdir(parents=True,exist_ok=True)
    files=list(p.glob("*.csv"))
    return {"platform":"FTMO","available":len(files)>0,"mode":"ACCOUNT_REPORT_INGESTION_ONLY","watch_dir":str(p),"csv_files":len(files),"real_trading":"FORBIDDEN"}

def run():
    out=Path("reports/P13.8_PLATFORM_CONNECTORS")
    out.mkdir(parents=True,exist_ok=True)
    status={
        "STATUS":"P13.8_PLATFORM_CONNECTORS_IMPLEMENTED",
        "MT5":mt5_probe(),
        "PROFIT":profit_probe(),
        "FTMO":ftmo_probe(),
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"P13.8_platform_connector_status.json").write_text(json.dumps(status,indent=2,ensure_ascii=False),encoding="utf-8")
    return status

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))

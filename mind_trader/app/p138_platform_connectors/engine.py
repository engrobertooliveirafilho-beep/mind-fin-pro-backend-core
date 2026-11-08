import json, csv
from pathlib import Path
from datetime import datetime, UTC

def mt5_probe():
    raise PermissionError("ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED")

def profit_probe(path="data/incoming/profit"):
    p=Path(path)
    files=list(p.glob("*.csv")) if p.is_dir() else []
    return {"platform":"PROFIT","available":len(files)>0,"mode":"LOCAL_EXPORT_BRIDGE","watch_dir":str(p),"csv_files":len(files)}

def ftmo_probe(path="data/incoming/ftmo"):
    p=Path(path)
    files=list(p.glob("*.csv")) if p.is_dir() else []
    return {"platform":"FTMO","available":len(files)>0,"mode":"ACCOUNT_REPORT_INGESTION_ONLY","watch_dir":str(p),"csv_files":len(files),"real_trading":"FORBIDDEN"}

def run():
    mt5_probe()
    # Fail closed before touching any local report or bridge directories.
    raise PermissionError("ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED")

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))

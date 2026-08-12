import json, shutil, time
from pathlib import Path
from datetime import datetime, UTC

OUT=Path("reports/P1002_RUNTIME_HEALTH_MONITOR")
LOGS=Path("reports/P1000_AUTONOMOUS_DAILY_SCHEDULER/logs")
BLOCKS={"REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    total, used, free = shutil.disk_usage(".")
    logs=list(LOGS.glob("*.log")) if LOGS.exists() else []
    latest=max(logs,key=lambda p:p.stat().st_mtime) if logs else None
    report={
        "STATUS":"P1002_RUNTIME_HEALTH_MONITOR_COMPLETED",
        "DISK_FREE_GB":round(free/1024**3,2),
        "LOGS_TOTAL":len(logs),
        "LATEST_LOG":str(latest) if latest else None,
        "HEALTH":"GREEN" if free/1024**3 > 5 else "YELLOW",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p1002_health_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__": run()

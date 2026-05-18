from datetime import datetime, timezone

RUNTIME_STATE={}

def set_runtime_state(key:str, value:str):
    RUNTIME_STATE[key]={
        "value":value,
        "updated_at":datetime.now(timezone.utc).isoformat()
    }
    return {"status":"ok","key":key,"state":RUNTIME_STATE[key]}

def runtime_state_report():
    return {"status":"ok","keys_total":len(RUNTIME_STATE),"state":RUNTIME_STATE}

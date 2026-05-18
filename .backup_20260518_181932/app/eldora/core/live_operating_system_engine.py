from datetime import datetime, timezone

OS_RUNTIME=[]

def runtime_signal(environment:str, signal:str):
    item = {
        "environment":environment,
        "signal":signal,
        "runtime_state":"active",
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    OS_RUNTIME.append(item)

    return {
        "status":"ok",
        "runtime":item
    }

def runtime_report():
    return {
        "status":"ok",
        "runtime_events_total":len(OS_RUNTIME),
        "runtime_events":OS_RUNTIME[-100:]
    }

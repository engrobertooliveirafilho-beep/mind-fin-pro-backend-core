from datetime import datetime, timezone

WEBSOCKET_EVENTS=[]

def websocket_cognition_signal(channel:str, message:str):
    item={
        "channel":channel,
        "message":message,
        "mode":"websocket_ready",
        "timestamp":datetime.now(timezone.utc).isoformat()
    }
    WEBSOCKET_EVENTS.append(item)
    return {"status":"ok","signal":item}

def websocket_report():
    return {"status":"ok","signals_total":len(WEBSOCKET_EVENTS),"signals":WEBSOCKET_EVENTS[-100:]}

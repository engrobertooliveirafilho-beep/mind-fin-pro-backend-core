from datetime import datetime, timezone

EVENT_STREAM=[]

def publish_event(stream:str, event:str):
    item = {
        "stream":stream,
        "event":event,
        "status":"published",
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    EVENT_STREAM.append(item)

    return {
        "status":"ok",
        "event":item
    }

def stream_report():
    return {
        "status":"ok",
        "events_total":len(EVENT_STREAM),
        "events":EVENT_STREAM[-100:]
    }

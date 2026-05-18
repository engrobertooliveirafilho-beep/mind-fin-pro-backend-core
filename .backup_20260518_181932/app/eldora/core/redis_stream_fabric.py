import os, json, uuid
from datetime import datetime, timezone

try:
    import redis
except Exception:
    redis = None

MEMORY_STREAM=[]

def _client():
    url=os.getenv("REDIS_URL")
    if not url or redis is None:
        return None
    return redis.from_url(url, decode_responses=True)

def publish_stream(stream:str, event:str, payload:dict|None=None):
    item={
        "event_id":str(uuid.uuid4()),
        "stream":stream,
        "event":event,
        "payload":payload or {},
        "timestamp":datetime.now(timezone.utc).isoformat()
    }
    client=_client()
    if not client:
        MEMORY_STREAM.append(item)
        return {"status":"ok","backend":"memory","event":item}
    client.xadd(stream, {"event":event, "payload":json.dumps(payload or {}), "timestamp":item["timestamp"]})
    return {"status":"ok","backend":"redis","event":item}

def stream_report():
    return {"status":"ok","backend":"redis" if _client() else "memory","events_total":len(MEMORY_STREAM),"events":MEMORY_STREAM[-100:]}

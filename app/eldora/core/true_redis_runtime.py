import os, json, uuid
from datetime import datetime, timezone

try:
    import redis
except Exception:
    redis = None

MEMORY_FALLBACK=[]

def redis_client():
    url=os.getenv("REDIS_URL")
    if not url or redis is None:
        return None
    return redis.from_url(url, decode_responses=True)

def publish_true_stream(stream:str, event:str, payload:dict|None=None):
    payload=payload or {}
    item={
        "event_id":str(uuid.uuid4()),
        "stream":stream,
        "event":event,
        "payload":payload,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }
    client=redis_client()
    if not client:
        MEMORY_FALLBACK.append(item)
        return {"status":"ok","backend":"memory_fallback","event":item}
    event_id=client.xadd(stream,{
        "event_id":item["event_id"],
        "event":event,
        "payload":json.dumps(payload),
        "timestamp":item["timestamp"]
    })
    item["redis_event_id"]=event_id
    return {"status":"ok","backend":"redis","event":item}

def true_stream_report(stream:str="eldora.true.events", count:int=20):
    client=redis_client()
    if not client:
        return {"status":"ok","backend":"memory_fallback","events_total":len(MEMORY_FALLBACK),"events":MEMORY_FALLBACK[-count:]}
    items=client.xrevrange(stream, count=count)
    return {"status":"ok","backend":"redis","events_total":len(items),"events":items}

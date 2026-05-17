import os
import json
import uuid
from datetime import datetime, timezone

try:
    import redis
except Exception as e:
    redis = None
    IMPORT_ERROR = str(e)
else:
    IMPORT_ERROR = None

MEMORY_FALLBACK = []
LAST_REDIS_ERROR = None

def redis_client():
    global LAST_REDIS_ERROR

    try:
        url = os.getenv("REDIS_URL")

        if not url:
            LAST_REDIS_ERROR = "REDIS_URL missing"
            return None

        if redis is None:
            LAST_REDIS_ERROR = f"redis import failed: {IMPORT_ERROR}"
            return None

        client = redis.from_url(
            url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            ssl_cert_reqs=None if url.startswith("rediss://") else "required"
        )

        client.ping()
        LAST_REDIS_ERROR = None
        return client

    except Exception as e:
        LAST_REDIS_ERROR = str(e)
        return None

def redis_last_error():
    return LAST_REDIS_ERROR

def publish_true_stream(stream:str, event:str, payload:dict|None=None):
    payload = payload or {}

    item = {
        "event_id": str(uuid.uuid4()),
        "stream": stream,
        "event": event,
        "payload": payload,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    try:
        client = redis_client()

        if client is None:
            MEMORY_FALLBACK.append(item)
            return {
                "status":"ok",
                "backend":"memory_fallback",
                "redis_error": redis_last_error(),
                "event":item
            }

        redis_event_id = client.xadd(
            stream,
            {
                "event_id": item["event_id"],
                "event": event,
                "payload": json.dumps(payload),
                "timestamp": item["timestamp"]
            }
        )

        item["redis_event_id"] = redis_event_id

        return {
            "status":"ok",
            "backend":"redis",
            "event":item
        }

    except Exception as e:
        MEMORY_FALLBACK.append(item)
        return {
            "status":"ok",
            "backend":"memory_fallback",
            "redis_error": str(e),
            "event": item
        }

def true_stream_report(stream:str="eldora.true.events", count:int=20):
    try:
        client = redis_client()

        if client is None:
            return {
                "status":"ok",
                "backend":"memory_fallback",
                "redis_error": redis_last_error(),
                "events_total":len(MEMORY_FALLBACK),
                "events":MEMORY_FALLBACK[-count:]
            }

        items = client.xrevrange(stream, count=count)

        return {
            "status":"ok",
            "backend":"redis",
            "events_total":len(items),
            "events":items
        }

    except Exception as e:
        return {
            "status":"ok",
            "backend":"memory_fallback",
            "redis_error":str(e),
            "events_total":len(MEMORY_FALLBACK),
            "events":MEMORY_FALLBACK[-count:]
        }

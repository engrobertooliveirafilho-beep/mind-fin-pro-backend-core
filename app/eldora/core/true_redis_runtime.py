import os
import json
import uuid
from datetime import datetime, timezone

try:
    import redis
except Exception:
    redis = None

MEMORY_FALLBACK = []

def redis_client():
    try:
        url = os.getenv("REDIS_URL")

        if not url:
            return None

        if redis is None:
            return None

        return redis.from_url(
            url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )

    except Exception:
        return None

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

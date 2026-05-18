import os, redis
from fastapi import APIRouter, HTTPException, Header

router = APIRouter(prefix="/eldora/redis-live", tags=["eldora-redis-live"])

def _guard(token):
    expected = os.getenv("ADMIN_ACTIVATION_TOKEN")
    if expected and token != expected:
        raise HTTPException(403, "admin token invalid")
    return True

def _redis():
    url = os.getenv("REDIS_URL")
    if not url:
        raise HTTPException(500, "REDIS_URL missing")
    return redis.from_url(url, decode_responses=True)

@router.get("/ping")
def ping(x_admin_token: str | None = Header(default=None)):
    _guard(x_admin_token)
    r = _redis()
    return {"redis_ping": bool(r.ping()), "backend": "redis"}

@router.post("/stream/publish-read")
def publish_read(payload: dict, x_admin_token: str | None = Header(default=None)):
    _guard(x_admin_token)
    r = _redis()
    stream = payload.get("stream", "eldora:live_gate")
    event = {"type": payload.get("type", "redis_stream_gate"), "payload": str(payload.get("payload", {}))}
    event_id = r.xadd(stream, event)
    rows = r.xrevrange(stream, count=1)
    return {"stream_live": True, "stream": stream, "event_id": event_id, "last_event": rows[0] if rows else None}

@router.post("/dlq/publish")
def dlq(payload: dict, x_admin_token: str | None = Header(default=None)):
    _guard(x_admin_token)
    r = _redis()
    stream = "eldora:dlq"
    event_id = r.xadd(stream, {"error": payload.get("error", "unknown"), "payload": str(payload)})
    return {"dlq_live": True, "stream": stream, "event_id": event_id}

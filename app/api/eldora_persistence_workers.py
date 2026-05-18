from fastapi import APIRouter
from app.eldora.persistence.provider import EldoraPersistenceProvider
from app.eldora.workers.registry import worker_registry, retry_with_backoff, dead_letter_event

router = APIRouter(prefix="/eldora/persistence-workers", tags=["eldora-persistence-workers"])

@router.get("/health")
def health():
    return {"STATUS_FINAL": "ELDORA_PERSISTENCE_WORKERS_READY", "persistence": EldoraPersistenceProvider().health(), "workers": worker_registry()}

@router.post("/event/build")
def build_event(payload: dict):
    return EldoraPersistenceProvider().build_event(
        payload.get("tenant_id","default"),
        payload.get("user_id","anonymous"),
        payload.get("event_type","unknown"),
        payload.get("payload",{}),
        payload.get("idempotency_key")
    )

@router.post("/dlq")
def dlq(payload: dict):
    return dead_letter_event(payload.get("stream","unknown"), payload.get("event_id","unknown"), payload.get("error","unknown"), payload.get("payload",{}))

@router.get("/backoff/{attempt}")
def backoff(attempt: int):
    return {"attempt": attempt, "delay_seconds": retry_with_backoff(attempt)}

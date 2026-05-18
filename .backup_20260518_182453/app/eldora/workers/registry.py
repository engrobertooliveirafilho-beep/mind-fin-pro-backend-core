WORKER_STREAMS = {
    "acquisition_worker": "eldora:acquisition",
    "trial_expiration_worker": "eldora:trial_expiration",
    "retention_worker": "eldora:retention",
    "growth_campaign_worker": "eldora:growth_campaign",
    "voice_session_worker": "eldora:voice_session",
    "browser_task_worker": "eldora:browser_task",
    "revenue_event_worker": "eldora:revenue_event"
}

def worker_registry():
    return {"workers": WORKER_STREAMS, "count": len(WORKER_STREAMS), "redis_streams_ready": True}

def retry_with_backoff(attempt: int, base_seconds: int = 2):
    return min(300, base_seconds * (2 ** max(0, attempt - 1)))

def dead_letter_event(stream: str, event_id: str, error: str, payload: dict):
    return {"dlq": True, "stream": stream, "event_id": event_id, "error": error, "payload": payload}

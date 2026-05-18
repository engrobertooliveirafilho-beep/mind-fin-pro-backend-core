from app.eldora.persistence.provider import EldoraPersistenceProvider
from app.eldora.workers.registry import worker_registry, retry_with_backoff, dead_letter_event

def test_persistence_health_does_not_declare_live():
    assert EldoraPersistenceProvider().health()["live_connection_declared"] is False

def test_event_builder_has_idempotency():
    ev = EldoraPersistenceProvider().build_event("t1","u1","message",{})
    assert "idempotency_key" in ev

def test_worker_registry_count():
    assert worker_registry()["count"] == 7

def test_backoff():
    assert retry_with_backoff(3) == 8

def test_dlq():
    assert dead_letter_event("s","1","err",{})["dlq"] is True

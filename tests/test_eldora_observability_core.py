from app.eldora.core.dependency_container import container
from app.eldora.core.audit_ledger import audit_event, audit_report
from app.eldora.core.telemetry_runtime import telemetry_event
from app.eldora.core.structured_logger import log
from app.eldora.core.runtime_metrics import increment, metrics_report
from app.eldora.core.event_bus import publish, event_bus_report

def test_dependency_container():
    assert container.register("x", {"ok": True}) is True
    assert container.get("x")["ok"] is True

def test_audit_ledger():
    audit_event("test_event")
    assert audit_report()["events_count"] >= 1

def test_telemetry_runtime():
    event = telemetry_event("test")
    assert event["correlation_id"]

def test_structured_logger():
    item = log("info", "ok")
    assert item["level"] == "INFO"

def test_runtime_metrics():
    increment("requests_total")
    assert metrics_report()["metrics"]["requests_total"] >= 1

def test_event_bus():
    publish("test.topic", {"ok": True})
    assert event_bus_report()["events_count"] >= 1

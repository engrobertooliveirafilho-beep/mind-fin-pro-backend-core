from app.eldora.core.persistent_event_store import save_audit_event, save_event, audit_store_report

def test_persistent_audit_fallback():
    result = save_audit_event("test_persistent_audit", payload={"ok": True})
    assert result["saved"] is True
    assert result["backend"] in ("memory", "postgres")

def test_persistent_event_fallback():
    result = save_event("test.topic", {"ok": True})
    assert result["saved"] is True
    assert result["backend"] in ("memory", "postgres")

def test_store_report():
    assert audit_store_report()["status"] == "ok"

def test_bulk_capability_control_router_imports():
    from app.api.mind_trader_bulk_capability_control import router
    assert router is not None


def test_bulk_capability_control_disabled(monkeypatch):
    monkeypatch.delenv("MIND_TRADER_BULK_CAPABILITY_GATE", raising=False)

    from app.api.mind_trader_bulk_capability_control import bulk_capability_health, bulk_capability_run

    h = bulk_capability_health()
    assert h["status"] == "OK"
    assert h["gate_enabled"] is False
    assert h["mode"] == "PAPER_ONLY"

    out = bulk_capability_run({"source": "P2338X14"})
    assert out["status"] == "DISABLED"
    assert out["real_orders"] == "FORBIDDEN"
    assert out["ftmo_real"] == "FORBIDDEN"


def test_bulk_capability_control_enabled(monkeypatch):
    monkeypatch.setenv("MIND_TRADER_BULK_CAPABILITY_GATE", "1")

    from app.api.mind_trader_bulk_capability_control import bulk_capability_run

    out = bulk_capability_run({"source": "P2338X14", "mode": "PAPER_ONLY"})
    assert out["status"] == "ENABLED"
    assert out["mode"] == "PAPER_ONLY"
    assert out["real_orders"] == "FORBIDDEN"
    assert out["ftmo_real"] == "FORBIDDEN"
    assert out["bulk_capabilities"]["imports_ok"] == out["bulk_capabilities"]["modules_total"]

def test_bulk_capability_gate_disabled_by_default(monkeypatch):
    monkeypatch.delenv("MIND_TRADER_BULK_CAPABILITY_GATE", raising=False)

    from app.runtime.mind_trader_bulk_capability_gate import run_gate, health

    h = health()
    assert h["status"] == "OK"
    assert h["gate_enabled"] is False
    assert h["mode"] == "PAPER_ONLY"
    assert h["real_orders"] == "FORBIDDEN"
    assert h["ftmo_real"] == "FORBIDDEN"
    assert h["bulk_modules_total"] >= 1

    out = run_gate({"source": "P2338X13"})
    assert out["status"] == "DISABLED"
    assert out["real_orders"] == "FORBIDDEN"
    assert out["ftmo_real"] == "FORBIDDEN"


def test_bulk_capability_gate_enabled(monkeypatch):
    monkeypatch.setenv("MIND_TRADER_BULK_CAPABILITY_GATE", "1")

    from app.runtime.mind_trader_bulk_capability_gate import run_gate, health

    h = health()
    assert h["status"] == "OK"
    assert h["gate_enabled"] is True
    assert h["bulk_imports_ok"] == h["bulk_modules_total"]

    out = run_gate({"source": "P2338X13", "mode": "PAPER_ONLY"})
    assert out["status"] == "ENABLED"
    assert out["mode"] == "PAPER_ONLY"
    assert out["real_orders"] == "FORBIDDEN"
    assert out["ftmo_real"] == "FORBIDDEN"
    assert out["bulk_capabilities"]["imports_ok"] == out["bulk_capabilities"]["modules_total"]

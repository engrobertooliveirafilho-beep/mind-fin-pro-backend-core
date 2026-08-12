def test_institutional_gate_disabled_by_default(monkeypatch):
    monkeypatch.delenv("MIND_TRADER_INSTITUTIONAL_GATE", raising=False)

    from app.runtime.mind_trader_institutional_gate import run_gate, health

    h = health()
    assert h["status"] == "OK"
    assert h["gate_enabled"] is False

    out = run_gate({"source": "P2338X8"})
    assert out["status"] == "DISABLED"
    assert out["mode"] == "PAPER_ONLY"
    assert out["real_orders"] == "FORBIDDEN"
    assert out["ftmo_real"] == "FORBIDDEN"


def test_institutional_gate_enabled(monkeypatch):
    monkeypatch.setenv("MIND_TRADER_INSTITUTIONAL_GATE", "1")

    from app.runtime.mind_trader_institutional_gate import run_gate, health

    h = health()
    assert h["status"] == "OK"
    assert h["gate_enabled"] is True

    out = run_gate({"source": "P2338X8"})
    assert out["status"] == "ENABLED"
    assert out["mode"] == "PAPER_ONLY"
    assert out["real_orders"] == "FORBIDDEN"
    assert out["ftmo_real"] == "FORBIDDEN"
    assert "institutional" in out
    assert out["institutional"]["imports_ok"] == out["institutional"]["modules_total"]

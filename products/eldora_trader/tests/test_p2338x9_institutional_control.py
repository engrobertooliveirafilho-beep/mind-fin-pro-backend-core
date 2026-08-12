def test_institutional_control_router_imports():
    from app.api.mind_trader_institutional_control import router
    assert router is not None


def test_institutional_control_health_disabled(monkeypatch):
    monkeypatch.delenv("MIND_TRADER_INSTITUTIONAL_GATE", raising=False)

    from app.api.mind_trader_institutional_control import institutional_health, institutional_run

    h = institutional_health()
    assert h["status"] == "OK"
    assert h["gate_enabled"] is False
    assert h["mode"] == "PAPER_ONLY"

    out = institutional_run({"source": "P2338X9"})
    assert out["status"] == "DISABLED"
    assert out["real_orders"] == "FORBIDDEN"
    assert out["ftmo_real"] == "FORBIDDEN"


def test_institutional_control_run_enabled(monkeypatch):
    monkeypatch.setenv("MIND_TRADER_INSTITUTIONAL_GATE", "1")

    from app.api.mind_trader_institutional_control import institutional_run

    out = institutional_run({"source": "P2338X9"})
    assert out["status"] == "ENABLED"
    assert out["mode"] == "PAPER_ONLY"
    assert out["real_orders"] == "FORBIDDEN"
    assert out["ftmo_real"] == "FORBIDDEN"
    assert out["institutional"]["imports_ok"] == out["institutional"]["modules_total"]

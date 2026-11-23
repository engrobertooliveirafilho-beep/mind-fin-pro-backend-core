from types import SimpleNamespace
from app.runtime import mind_trader_institutional_wiring as wiring


def test_institutional_wiring_degraded_when_import_fails(monkeypatch):
    monkeypatch.setattr(wiring, "MODULES", ["missing.module"])
    def fail(_name):
        raise ImportError("missing original runtime")
    monkeypatch.setattr(wiring.importlib, "import_module", fail)
    result = wiring.run_institutional_wiring({})
    assert result["status"] == "DEGRADED"
    assert result["imports_ok"] == 0
    assert result["runs_ok"] == 0


def test_institutional_wiring_degraded_when_run_fails(monkeypatch):
    monkeypatch.setattr(wiring, "MODULES", ["fake.module"])
    def fail_run(_payload):
        raise RuntimeError("runtime unavailable")
    monkeypatch.setattr(wiring.importlib, "import_module", lambda _name: SimpleNamespace(run=fail_run))
    result = wiring.run_institutional_wiring({})
    assert result["status"] == "DEGRADED"
    assert result["imports_ok"] == 1
    assert result["runs_ok"] == 0
    assert wiring.health()["status"] == "DEGRADED"


def test_institutional_wiring_operational_only_when_runtime_executes(monkeypatch):
    monkeypatch.setattr(wiring, "MODULES", ["fake.module"])
    monkeypatch.setattr(wiring.importlib, "import_module", lambda _name: SimpleNamespace(run=lambda _payload: {"mode": "PAPER_ONLY"}))
    result = wiring.run_institutional_wiring({})
    assert result["status"] == "operational"
    assert result["imports_ok"] == 1
    assert result["runs_ok"] == 1


def test_health_never_executes_trading_motor(monkeypatch):
    monkeypatch.setattr(wiring, "MODULES", ["fake.module"])
    called = []
    def dangerous_run(_payload=None):
        called.append("RUN")
        raise RuntimeError("run must not execute")
    monkeypatch.setattr(wiring.importlib, "import_module", lambda _name: SimpleNamespace(run=dangerous_run, health=lambda: {"status": "OK"}))
    status = wiring.health()
    assert called == []
    assert status["status"] == "DEGRADED"
    assert status["imports_ok"] == 1
    assert status["runs_ok"] == 0
    assert status["health_ok"] == 1


def test_internal_typeerror_does_not_retry_motor_without_payload(monkeypatch):
    monkeypatch.setattr(wiring, "MODULES", ["fake.module"])
    calls = []
    def run(payload=None):
        calls.append(payload)
        raise TypeError("failure inside trading motor")
    monkeypatch.setattr(wiring.importlib, "import_module", lambda _name: SimpleNamespace(run=run))
    result = wiring.run_institutional_wiring({"mode": "PAPER_ONLY"})
    assert result["status"] == "DEGRADED"
    assert result["runs_ok"] == 0
    assert calls == [{"mode": "PAPER_ONLY"}]

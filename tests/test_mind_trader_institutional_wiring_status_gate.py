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
    monkeypatch.setattr(wiring.importlib, "import_module", lambda _name: SimpleNamespace(run=lambda _payload: {"status": "OPERATIONAL", "mode": "PAPER_ONLY"}))
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


def test_blocked_motor_result_is_not_operational(monkeypatch):
    monkeypatch.setattr(wiring, "MODULES", ["fake.module"])
    monkeypatch.setattr(wiring.importlib, "import_module", lambda _name: SimpleNamespace(run=lambda _payload: {"status": "BLOCKED", "reason": "NO_SYMBOL_LINEAGE"}))
    result = wiring.run_institutional_wiring({"mode": "PAPER_ONLY"})
    assert result["status"] == "DEGRADED"
    assert result["runs_ok"] == 0
    assert result["results"][0]["run_result"]["reason"] == "NO_SYMBOL_LINEAGE"


def test_forbidden_execution_payload_blocked_before_motor_import(monkeypatch):
    def forbidden_import(_name):
        raise AssertionError("motor import must never occur")
    monkeypatch.setattr(wiring.importlib, "import_module", forbidden_import)
    for payload in (
        {"mode": "LIVE"}, {"real_orders": "ALLOWED"},
        {"ftmo_real": "ALLOWED"}, [], "PAPER_ONLY",
    ):
        result = wiring.run_institutional_wiring(payload)
        assert result["status"] == "BLOCKED"
        assert result["reason"] == "PAPER_ONLY_EXECUTION_GATE"
        assert result["imports_ok"] == 0
        assert result["runs_ok"] == 0


def test_ambiguous_motor_results_never_certify_operation(monkeypatch):
    monkeypatch.setattr(wiring, "MODULES", ["fake.module"])
    for value in (None, True, "OK", [], {}, {"mode": "PAPER_ONLY"}, {"status": "NOT_IMPLEMENTED"}):
        monkeypatch.setattr(wiring.importlib, "import_module", lambda _name: SimpleNamespace(run=lambda _payload: value))
        result = wiring.run_institutional_wiring({"mode": "PAPER_ONLY"})
        assert result["status"] == "DEGRADED"
        assert result["runs_ok"] == 0


def test_motor_claiming_live_execution_never_certifies_operation(monkeypatch):
    monkeypatch.setattr(wiring, "MODULES", ["fake.module"])
    for response in (
        {"status": "OPERATIONAL", "mode": "LIVE"},
        {"status": "PASS", "real_orders": "ALLOWED"},
        {"status": "SUCCESS", "ftmo_real": "ALLOWED"},
    ):
        monkeypatch.setattr(wiring.importlib, "import_module", lambda _name: SimpleNamespace(run=lambda _payload: response))
        result = wiring.run_institutional_wiring({"mode": "PAPER_ONLY"})
        assert result["status"] == "DEGRADED"
        assert result["runs_ok"] == 0


def test_zero_argument_motor_cannot_bypass_paper_lock(monkeypatch):
    monkeypatch.setattr(wiring, "MODULES", ["fake.module"])
    called = []
    def unsafe_run():
        called.append("EXECUTED")
        return {"status": "OPERATIONAL", "mode": "LIVE"}
    monkeypatch.setattr(wiring.importlib, "import_module", lambda _name: SimpleNamespace(run=unsafe_run))
    result = wiring.run_institutional_wiring({"mode": "PAPER_ONLY"})
    assert called == []
    assert result["status"] == "DEGRADED"
    assert result["runs_ok"] == 0
    assert "PAPER_ONLY_CONTRACT_NOT_PROPAGATED" in result["results"][0]["error"]

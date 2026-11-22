from app.runtime.p2101_2110_autonomous_paper_operations import AutoDiagnostics

def _state(heartbeat=1):
    return {"runtime_status": "RUNNING", "heartbeat": heartbeat}

def test_p2106_missing_dependency_is_fail_not_exception():
    d = AutoDiagnostics().evaluate({}, _state())
    assert d.status == "FAIL"
    assert d.payload["p2071_certified"] is False

def test_p2106_partial_dependency_is_fail():
    d = AutoDiagnostics().evaluate({"p2071": {"status": "PASS"}}, _state())
    assert d.status == "FAIL"

def test_p2106_rejects_string_heartbeat_without_type_error():
    deps = {k: {"status": "PASS"} for k in ("p2071", "p2081", "p2091")}
    d = AutoDiagnostics().evaluate(deps, _state("alive"))
    assert d.status == "FAIL"

def test_p2106_valid_paper_diagnostics():
    deps = {k: {"status": "PASS"} for k in ("p2071", "p2081", "p2091")}
    d = AutoDiagnostics().evaluate(deps, _state(123))
    assert d.status == "PASS"

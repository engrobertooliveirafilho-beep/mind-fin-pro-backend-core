from app.runtime.ready_capability_bridge import ready_capability_report


def test_p473b_ready_bridge_imports_all_modules():
    out = ready_capability_report("p473b_test", "teste")
    assert out["summary"]["total"] == 3
    assert out["summary"]["import_ok"] == 3


def test_p473b_ready_bridge_has_at_least_one_successful_call():
    out = ready_capability_report("p473b_test", "teste")
    assert out["summary"]["successful_calls"] >= 1

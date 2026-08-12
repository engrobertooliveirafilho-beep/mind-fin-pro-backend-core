from app.runtime.capability_recovery_bridge import capability_recovery_report


def test_p472b_capability_bridge_imports_top5():
    out = capability_recovery_report("p472b_test", "teste")
    assert out["summary"]["total"] == 5
    assert out["summary"]["import_ok"] >= 5


def test_p472b_capability_bridge_has_successful_call():
    out = capability_recovery_report("p472b_test", "teste")
    assert out["summary"]["with_successful_calls"] >= 1

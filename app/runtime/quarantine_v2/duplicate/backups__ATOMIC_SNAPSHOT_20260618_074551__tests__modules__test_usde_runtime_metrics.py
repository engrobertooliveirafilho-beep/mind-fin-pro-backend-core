from app.modules.usde_core.runtime_metrics import RuntimeMetrics

def test_runtime_metrics():
    r=RuntimeMetrics().snapshot(
        {"modules":27,"tests":22}
    )

    assert r["runtime_status"]=="ONLINE"
    assert r["modules"]==27

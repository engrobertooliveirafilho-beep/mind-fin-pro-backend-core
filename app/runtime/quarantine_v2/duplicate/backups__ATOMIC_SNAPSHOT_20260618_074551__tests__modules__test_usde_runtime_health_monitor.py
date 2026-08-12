from app.modules.usde_core.runtime_health_monitor import RuntimeHealthMonitor

def test_runtime_health_monitor():
    r=RuntimeHealthMonitor().check(
        {"runtime_status":"ONLINE","modules":27}
    )

    assert r["status"]=="HEALTHY"

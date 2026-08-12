from app.modules.usde_core.runtime_integration_binder import RuntimeIntegrationBinder

def test_runtime_integration_binder():
    r=RuntimeIntegrationBinder().bind_plan()

    assert r["status"]=="BIND_PLAN_READY"
    assert "runtime" in r["targets"]
    assert "eldora" in r["targets"]

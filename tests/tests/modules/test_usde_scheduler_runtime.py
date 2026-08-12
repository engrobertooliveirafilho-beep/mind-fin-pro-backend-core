from app.modules.usde_core.scientific_scheduler_runtime import ScientificSchedulerRuntime

def test_scheduler_runtime():
    r=ScientificSchedulerRuntime().run_cycle(
        {"events":1000}
    )

    assert r["status"]=="COMPLETED"
    assert r["executed"]==5

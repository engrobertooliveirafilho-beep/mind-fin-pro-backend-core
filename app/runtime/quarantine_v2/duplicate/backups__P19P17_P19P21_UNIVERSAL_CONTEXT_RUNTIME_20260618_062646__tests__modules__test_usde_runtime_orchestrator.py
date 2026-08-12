from app.modules.usde_core.scientific_runtime_orchestrator import ScientificRuntimeOrchestrator

def test_runtime_orchestrator():
    r=ScientificRuntimeOrchestrator().run(
        "test",
        "runtime validation"
    )

    assert "hypothesis" in r
    assert "experiment" in r
    assert "evidence" in r
    assert "decision" in r

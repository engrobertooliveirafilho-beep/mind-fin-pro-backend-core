from app.eldora.core.self_healing_engine import trigger_recovery
from app.eldora.core.supervisor_swarm import supervisor_report
from app.eldora.core.recursive_execution_engine import recursive_execute

def test_self_healing():
    r = trigger_recovery("runtime")
    assert r["status"] == "ok"

def test_supervisor_swarm():
    r = supervisor_report()
    assert r["supervisors_total"] >= 1

def test_recursive_execution():
    r = recursive_execute("validate_runtime", 1, 2)
    assert r["status"] == "ok"

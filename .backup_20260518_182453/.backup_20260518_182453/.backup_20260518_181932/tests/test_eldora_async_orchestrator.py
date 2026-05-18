from app.eldora.core.task_engine import create_task, get_task
from app.eldora.core.agent_orchestrator import orchestrate
from app.eldora.core.distributed_runtime import distributed_runtime_report

def test_task_engine():
    task = create_task("unit_test")
    assert task["status"] == "queued"
    assert get_task(task["task_id"])["task_id"] == task["task_id"]

def test_agent_orchestrator():
    result = orchestrate("validate_system")
    assert result["tasks_created"] == 4

def test_distributed_runtime():
    report = distributed_runtime_report()
    assert report["nodes_total"] >= 1

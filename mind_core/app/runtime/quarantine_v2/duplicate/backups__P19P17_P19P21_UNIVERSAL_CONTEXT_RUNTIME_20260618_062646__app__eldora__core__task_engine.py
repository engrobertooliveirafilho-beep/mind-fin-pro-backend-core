from datetime import datetime, timezone

_TASKS = {}

def _now():
    return datetime.now(timezone.utc).isoformat()

def create_task(task_id, payload=None):
    task = {
        "task_id": task_id,
        "payload": payload or {},
        "status": "queued",
        "created_at": _now(),
        "updated_at": _now(),
    }
    _TASKS[task_id] = task
    return task

def get_task(task_id):
    return _TASKS.get(task_id, {"task_id": task_id, "status": "missing"})

def complete_task(task_id, result=None):
    task = _TASKS.get(task_id)
    if not task:
        return {"task_id": task_id, "status": "missing"}
    task["status"] = "completed"
    task["result"] = result or {}
    task["updated_at"] = _now()
    return task

def task_report():
    return {
        "status": "ok",
        "tasks_created": len(_TASKS),
        "queued": sum(1 for t in _TASKS.values() if t.get("status") == "queued"),
        "completed": sum(1 for t in _TASKS.values() if t.get("status") == "completed"),
    }

def task_engine_report():
    return task_report()

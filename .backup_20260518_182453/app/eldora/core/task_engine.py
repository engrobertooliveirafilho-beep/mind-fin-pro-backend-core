from datetime import datetime, timezone
import uuid

TASKS = {}

def create_task(task_type: str, payload: dict | None = None):
    task_id = str(uuid.uuid4())

    task = {
        "task_id": task_id,
        "task_type": task_type,
        "payload": payload or {},
        "status": "queued",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    TASKS[task_id] = task
    return task

def complete_task(task_id: str):
    if task_id in TASKS:
        TASKS[task_id]["status"] = "completed"
    return TASKS.get(task_id)

def get_task(task_id: str):
    return TASKS.get(task_id, {"status": "not_found"})

def task_report():
    return {
        "status": "ok",
        "tasks_total": len(TASKS),
        "tasks": list(TASKS.values())[-20:]
    }

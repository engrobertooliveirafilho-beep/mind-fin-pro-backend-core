from app.eldora.core.task_engine import create_task

AGENTS = {
    "memory_agent": {"status": "active"},
    "retrieval_agent": {"status": "active"},
    "reasoning_agent": {"status": "active"},
    "execution_agent": {"status": "active"}
}

def orchestrate(goal: str, payload: dict | None = None):
    tasks = [
        create_task("memory_analysis", {"goal": goal}),
        create_task("retrieval_execution", {"goal": goal}),
        create_task("reasoning_execution", {"goal": goal}),
        create_task("execution_runtime", {"goal": goal})
    ]

    return {
        "status": "ok",
        "goal": goal,
        "agents": AGENTS,
        "tasks_created": len(tasks),
        "tasks": tasks
    }

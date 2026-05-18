from datetime import datetime, timezone

RECURSIVE_STATE = {
    "executions": []
}

def recursive_execute(goal: str, depth: int = 1, max_depth: int = 3):
    node = {
        "goal": goal,
        "depth": depth,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    RECURSIVE_STATE["executions"].append(node)

    children = []

    if depth < max_depth:
        children.append(
            recursive_execute(goal, depth + 1, max_depth)
        )

    return {
        "status": "ok",
        "goal": goal,
        "depth": depth,
        "children": children
    }

def recursive_report():
    return {
        "status": "ok",
        "executions_total": len(RECURSIVE_STATE["executions"]),
        "executions": RECURSIVE_STATE["executions"][-20:]
    }

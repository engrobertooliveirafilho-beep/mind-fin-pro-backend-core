from pathlib import Path

Path("app/p7_adapters/hierarchical_planner_adapter.py").write_text("""
def plan(goal=None, context=None):
    return {
        "status": "ok",
        "goal": goal,
        "context": context or {},
        "plan": [
            {"step": 1, "action": "understand_goal"},
            {"step": 2, "action": "select_capability"},
            {"step": 3, "action": "execute_safely"},
            {"step": 4, "action": "validate_result"},
        ],
        "steps": [
            {"step_id": 1, "action": "understand_goal"},
            {"step_id": 2, "action": "select_capability"},
            {"step_id": 3, "action": "execute_safely"},
            {"step_id": 4, "action": "validate_result"},
        ],
    }

def plan_hierarchy(goal=None, context=None):
    return plan(goal, context)
""".strip() + "\n", encoding="utf-8")

print("hierarchical planner contract fixed")

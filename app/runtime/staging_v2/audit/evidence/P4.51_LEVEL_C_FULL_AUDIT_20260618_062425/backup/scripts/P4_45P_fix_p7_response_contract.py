from pathlib import Path

Path("app/p7_adapters/hierarchical_planner_adapter.py").write_text("""
from dataclasses import dataclass, field, asdict

@dataclass
class HierarchicalPlanRequest:
    user_intent: str
    goal: str
    context: dict = field(default_factory=dict)

@dataclass
class HierarchicalPlanResponse:
    status: str
    goal: str
    plan: list
    context: dict = field(default_factory=dict)

    def model_dump(self):
        return asdict(self)

    def dict(self):
        return asdict(self)

def plan_hierarchy(req):
    goal = getattr(req, "goal", None) or str(req)
    context = getattr(req, "context", {}) or {}
    return HierarchicalPlanResponse(
        status="ok",
        goal=goal,
        context=context,
        plan=[
            {"step": 1, "action": "understand_goal"},
            {"step": 2, "action": "select_capability"},
            {"step": 3, "action": "execute_safely"},
            {"step": 4, "action": "validate_result"},
        ],
    )

def plan(goal=None, context=None):
    req = HierarchicalPlanRequest(
        user_intent=str(goal or ""),
        goal=str(goal or ""),
        context=context or {},
    )
    return plan_hierarchy(req).model_dump()
""".strip() + "\n", encoding="utf-8")

print("P7 hierarchical planner response contract fixed")

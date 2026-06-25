from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass(frozen=True)
class HierarchicalPlanStep:
    level: int
    order: int
    title: str
    objective: str
    depends_on: List[int]
    risk: str
    validation: str

def generate_hierarchical_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    goal = str(payload.get("goal") or payload.get("prompt") or "undefined_goal")

    steps = [
        HierarchicalPlanStep(1, 1, "INTAKE", "Capture objective and constraints", [], "LOW", "input_present"),
        HierarchicalPlanStep(1, 2, "DECOMPOSITION", "Break goal into executable stages", [1], "LOW", "stages_created"),
        HierarchicalPlanStep(2, 3, "GUARDRAILS", "Apply safety, rollback and mutation constraints", [2], "MEDIUM", "constraints_checked"),
        HierarchicalPlanStep(2, 4, "EXECUTION_ORDER", "Sort stages by dependency and risk", [3], "LOW", "order_validated"),
        HierarchicalPlanStep(3, 5, "VALIDATION", "Define tests, telemetry and exit criteria", [4], "LOW", "validation_ready"),
    ]

    return {
        "capability": "HIERARCHICAL_PLANNING",
        "mode": "SHADOW",
        "goal": goal,
        "depth": 3,
        "step_count": len(steps),
        "plan": [s.__dict__ for s in steps],
        "execution_tree": {
            "root": goal,
            "children": [
                {"node": "INTAKE", "children": []},
                {"node": "DECOMPOSITION", "children": [
                    {"node": "GUARDRAILS", "children": [
                        {"node": "EXECUTION_ORDER", "children": [
                            {"node": "VALIDATION", "children": []}
                        ]}
                    ]}
                ]}
            ]
        },
        "runtime_modified": False,
        "response_modified": False,
        "runtime_authority_preserved": True,
    }

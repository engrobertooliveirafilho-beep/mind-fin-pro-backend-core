from app.planning.hierarchical_planner import HierarchicalPlanner
from .oversight_contracts import OversightInput
from .oversight_offline_gate import authorize


def guarded_plan(payload: OversightInput, goal: str, horizon: int):
    if payload.candidate_action != 'plan' or not authorize(payload):
        raise PermissionError('Offline planning denied')
    return HierarchicalPlanner().build_plan(goal, horizon)

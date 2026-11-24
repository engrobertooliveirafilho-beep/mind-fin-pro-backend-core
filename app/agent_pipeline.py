from app.agent.schemas import AgentPlan, AgentStep
from app.agent_executor import execute_plan
from app.p7_adapters.oversight_planner import guarded_plan


def calculate_plan(user, session_id, goal, expressions, *, oversight):
    if not isinstance(expressions, (list, tuple)) or not 1 <= len(expressions) <= 64:
        raise ValueError('Expected 1 to 64 explicit expressions')
    if any(not isinstance(x, str) for x in expressions):
        raise ValueError('Expressions must be strings')
    hierarchy = guarded_plan(oversight, goal, len(expressions))
    leaves = hierarchy.leaves()
    if len(leaves) != len(expressions):
        raise ValueError('Plan cardinality mismatch')
    plan = AgentPlan(summary=goal, steps=[AgentStep(tool='calc', input=x) for x in expressions])
    result = execute_plan(user, session_id, plan, goal, oversight=oversight)
    result['leaf_ids'] = [leaf.id for leaf in leaves]
    return result

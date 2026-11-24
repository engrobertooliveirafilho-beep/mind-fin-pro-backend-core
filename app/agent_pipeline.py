from app.mind.session_persist import get_history
from app.mind.vector_pipeline import query_similar
from app.modules.hyper_context_builder import HyperContextBuilder
from app.agent.schemas import AgentPlan, AgentStep
from app.agent_executor import execute_plan
from app.p7_adapters.oversight_planner import guarded_plan


def calculate_plan(user, session_id, goal, expressions, *, oversight):
    if not isinstance(expressions, (list, tuple)) or not 1 <= len(expressions) <= 64:
        raise ValueError('Expected 1 to 64 explicit expressions')
    if any(not isinstance(x, str) for x in expressions):
        raise ValueError('Expressions must be strings')
    hierarchy = guarded_plan(oversight, goal, len(expressions))
    if not isinstance(user, dict):
        raise ValueError('Explicit identity required')
    user_id = user.get('id')
    context = HyperContextBuilder()
    context.add_layer('session', {'messages': get_history(user_id, session_id, limit=10)})
    context.add_layer('lexical', {'matches': [item['text'] for item in query_similar(goal, 5, user_id, session_id)]})
    leaves = hierarchy.leaves()
    if len(leaves) != len(expressions):
        raise ValueError('Plan cardinality mismatch')
    plan = AgentPlan(summary=goal, steps=[AgentStep(tool='calc', input=x) for x in expressions])
    result = execute_plan(user, session_id, plan, goal, oversight=oversight)
    result['leaf_ids'] = [leaf.id for leaf in leaves]
    result['context'] = context.build()
    return result

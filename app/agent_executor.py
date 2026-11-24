from app.agent.schemas import AgentPlan
from app.p7_adapters.oversight_contracts import OversightInput
from app.cognitive_agent_kernel.dispatcher.offline_dispatch import dispatch_offline


def execute_plan(user, session_id, plan: AgentPlan, goal, *, oversight: OversightInput):
    """Validate and prepare only; no tool, database or LLM calls."""
    if not isinstance(user, dict) or not isinstance(user.get('id'), str) or not user['id'].strip():
        raise ValueError('Explicit identity required')
    if not isinstance(session_id, str) or not session_id.strip():
        raise ValueError('Explicit session required')
    if not isinstance(plan, AgentPlan):
        raise ValueError('Invalid plan')
    if dispatch_offline({'status': 'PLANNED'}, oversight) != 'AUTHORIZED_OFFLINE_PLANNING':
        raise PermissionError('Planning denied')
    validated = AgentPlan.model_validate(plan.model_dump())
    return {'goal': goal, 'plan': validated.model_dump(), 'results': [], 'history': [], 'status': 'PREPARED_NOT_EXECUTED'}

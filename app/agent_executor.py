from app.tools.calc import tool_calc
from app.agent.schemas import AgentPlan
from app.p7_adapters.oversight_contracts import OversightInput
from app.cognitive_agent_kernel.dispatcher.offline_dispatch import dispatch_offline


def execute_plan(user, session_id, plan: AgentPlan, goal, *, oversight: OversightInput):
    """Execute restricted arithmetic only; no database or LLM calls."""
    if not isinstance(user, dict) or not isinstance(user.get('id'), str) or not user['id'].strip():
        raise ValueError('Explicit identity required')
    if not isinstance(session_id, str) or not session_id.strip():
        raise ValueError('Explicit session required')
    if not isinstance(plan, AgentPlan):
        raise ValueError('Invalid plan')
    if dispatch_offline({'status': 'PLANNED'}, oversight) != 'AUTHORIZED_OFFLINE_PLANNING':
        raise PermissionError('Planning denied')
    validated = AgentPlan.model_validate(plan.model_dump())
    if not validated.steps or any(step.tool != 'calc' for step in validated.steps):
        raise PermissionError('Only nonempty arithmetic plans allowed')
    results = []
    for step in validated.steps:
        out = tool_calc(step.input)
        if not out['ok']:
            raise ValueError('Arithmetic step failed')
        results.append({'tool': step.tool, 'input': step.input, 'output': out})
    return {'goal': goal, 'plan': validated.model_dump(), 'results': results, 'history': [], 'status': 'COMPLETED_OFFLINE'}

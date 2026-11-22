"""Historical MIND agent metadata cannot authorize PAPER/real execution."""
from dataclasses import dataclass

@dataclass(frozen=True)
class AgentEvidence:
    agent_id: str
    registered: bool
    active_metadata: bool
    health_status: str
    steps_implemented: bool
    offline_tests_passed: bool
    paper_integration_passed: bool
    human_approved: bool

def certify_paper_agent(evidence: AgentEvidence) -> bool:
    if not isinstance(evidence, AgentEvidence):
        raise ValueError('structured agent evidence required')
    if not isinstance(evidence.agent_id, str) or not evidence.agent_id.strip():
        raise ValueError('agent identity required')
    if type(evidence.registered) is not bool or type(evidence.active_metadata) is not bool:
        raise ValueError('invalid registry metadata')
    for field in ('steps_implemented','offline_tests_passed','paper_integration_passed','human_approved'):
        if type(getattr(evidence, field)) is not bool:
            raise ValueError('invalid evidence flag: '+field)
    if not isinstance(evidence.health_status,str):
        raise ValueError('invalid health status')
    return (evidence.registered and evidence.active_metadata and evidence.health_status == 'healthy'
            and evidence.steps_implemented and evidence.offline_tests_passed
            and evidence.paper_integration_passed and evidence.human_approved)

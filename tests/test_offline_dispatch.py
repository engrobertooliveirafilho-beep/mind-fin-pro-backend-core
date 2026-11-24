import pytest
from app.cognitive_agent_kernel.dispatcher.offline_dispatch import dispatch_offline
from app.p7_adapters.oversight_contracts import OversightInput

@pytest.mark.parametrize('changes,expected', [({},'AUTHORIZED_OFFLINE_PLANNING'),({'execution_mode':'shadow'},'BLOCKED'),({'risk_flags':['risk']},'BLOCKED'),({'candidate_action':'inspect'},'BLOCKED'),({'confidence':None},'BLOCKED')])
def test_dispatch(changes, expected):
    payload = OversightInput(**({'candidate_action':'plan','reasoning_summary':'audit','execution_mode':'offline_analysis','confidence':.95} | changes))
    assert dispatch_offline({'status':'PLANNED'},payload) == expected

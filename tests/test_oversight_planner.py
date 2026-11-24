import pytest
from app.p7_adapters.oversight_contracts import OversightInput
from app.p7_adapters.oversight_planner import guarded_plan


def payload(**changes):
    return OversightInput(**({'candidate_action':'plan','reasoning_summary':'audit','execution_mode':'offline_analysis','confidence':.95} | changes))


def test_authorized_plan():
    assert len(guarded_plan(payload(), 'audit', 7).leaves()) == 7


@pytest.mark.parametrize('changes', [{'execution_mode':'shadow'}, {'candidate_action':'inspect'}, {'risk_flags':['risk']}, {'policy_constraints':['deny']}, {'confidence':.5}])
def test_denied_plan(changes):
    with pytest.raises(PermissionError):
        guarded_plan(payload(**changes), 'audit', 7)

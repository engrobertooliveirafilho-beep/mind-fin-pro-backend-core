import pytest
from app.agent_pipeline import calculate_plan
from app.p7_adapters.oversight_contracts import OversightInput


def run(expressions, **changes):
    payload = OversightInput(**({'candidate_action':'plan','reasoning_summary':'audit','execution_mode':'offline_analysis','confidence':.95} | changes))
    return calculate_plan({'id':'audit'}, 'session', 'audit', expressions, oversight=payload, execution_approved=True)


def test_chain():
    result = run(['2+3', '4*5'])
    assert result['status'] == 'COMPLETED_OFFLINE'
    assert [r['output']['result'] for r in result['results']] == [5, 20]
    assert len(set(result['leaf_ids'])) == 2


@pytest.mark.parametrize('changes', [{'execution_mode':'shadow'}, {'risk_flags':['risk']}])
def test_block(changes):
    with pytest.raises(PermissionError):
        run(['2+3'], **changes)


@pytest.mark.parametrize('expressions', [[], ['1/0'], ['1']*65])
def test_invalid(expressions):
    with pytest.raises(ValueError):
        run(expressions)


def test_missing_execution_approval():
    payload = OversightInput(candidate_action='plan', reasoning_summary='audit', execution_mode='offline_analysis', confidence=.95)
    with pytest.raises(PermissionError):
        calculate_plan({'id':'audit'}, 'session', 'audit', ['2+3'], oversight=payload)

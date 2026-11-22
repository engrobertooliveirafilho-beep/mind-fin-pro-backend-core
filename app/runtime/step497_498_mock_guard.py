"""Fail-closed classification of historical STEP497/498 mock-derived data."""
from collections.abc import Mapping

def classify_pipeline(payload, *, verified_live_source=False):
    if not isinstance(payload, Mapping) or type(verified_live_source) is not bool:
        raise ValueError('explicit pipeline evidence required')
    if payload.get('version') != 'step497-v1':
        return {'state':'UNVERIFIED','certified':False}
    # Historical step497-v1 uses hardcoded _mock_stages, _mock_next_actions and _mock_metrics.
    # A caller claim alone cannot override the known provenance of this version.
    return {'state':'HISTORICAL_MOCK_DATA','certified':False}

def classify_ceo_briefing(payload):
    if not isinstance(payload, Mapping):
        raise ValueError('briefing mapping required')
    if payload.get('version') != 'step498-v1':
        return {'state':'UNVERIFIED','certified':False}
    pipeline=payload.get('pipeline')
    if not isinstance(pipeline,Mapping):
        return {'state':'INCOMPLETE_DEPENDENCIES','certified':False}
    inner=classify_pipeline(pipeline)
    if inner['state']=='HISTORICAL_MOCK_DATA':
        return {'state':'MOCK_CONTAMINATED_BRIEFING','certified':False}
    return {'state':'UNVERIFIED_DEPENDENCIES','certified':False}


class MockDataBlocked(RuntimeError):
    """A recovered mock engine cannot serve certified PAPER decision data."""

def execute_paper_pipeline(engine):
    """Execute an explicit source engine and reject historical mock output."""
    if not callable(engine):
        raise ValueError('explicit engine callable required')
    # The recovered original STEP497 implementation is known to return mock metrics.\n    # Reject before invocation so a future side-effectful replacement cannot run.\n    if (getattr(engine, '__module__', None) ==\n            'recovered.finance_steps.step497_pipeline_engine_original' and\n            getattr(engine, '__name__', None) == 'get_business_pipeline_snapshot'):\n        raise MockDataBlocked('HISTORICAL_MOCK_DATA')\n    payload=engine()\n    state=classify_pipeline(payload)
    if not state['certified']:
        raise MockDataBlocked(state['state'])
    return payload

def execute_paper_briefing(engine):
    """Execute an explicit CEO engine and reject unverified or mock dependencies."""
    if not callable(engine):
        raise ValueError('explicit engine callable required')
    payload=engine()
    state=classify_ceo_briefing(payload)
    if not state['certified']:
        raise MockDataBlocked(state['state'])
    return payload

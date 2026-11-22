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
    """Unverified engines cannot execute on the PAPER decision boundary."""

def execute_paper_pipeline(engine):
    """Fail closed before executing any engine until trusted evidence is integrated."""
    if not callable(engine):
        raise ValueError('explicit engine callable required')
    raise MockDataBlocked('PAPER_PIPELINE_NOT_CERTIFIED')

def execute_paper_briefing(engine):
    """Fail closed before running mock or unverified executive dependencies."""
    if not callable(engine):
        raise ValueError('explicit engine callable required')
    raise MockDataBlocked('PAPER_CEO_DEPENDENCIES_NOT_CERTIFIED')

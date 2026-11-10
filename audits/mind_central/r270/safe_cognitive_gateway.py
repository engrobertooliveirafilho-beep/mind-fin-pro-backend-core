"""R270 isolated prevalidation wrapper for recovered cognitive engines; deny-only."""
from finite_scores import finite_score, InvalidScore

PURPOSE_DIMS = ('user_benefit','safety','long_term','cashflow','learning')
EXPLANATION_DIMS = ('purpose_alignment','reality_certainty','ethics')

class GateRejected(ValueError):
    pass

def _dict(value, name):
    if not isinstance(value, dict):
        raise GateRejected(f'{name}: INVALID_OBJECT')
    return value

def _scores(scores, dimensions):
    _dict(scores, 'scores')
    if set(scores) != set(dimensions):
        raise GateRejected('SCORE_DIMENSIONS_MISMATCH')
    try:
        return {key: finite_score(scores[key], name=key) for key in dimensions}
    except InvalidScore as e:
        raise GateRejected(str(e)) from e

def purpose(kernel, payload):
    _dict(payload, 'payload')
    normalized = _scores(payload.get('scores'), PURPOSE_DIMS)
    return kernel.evaluate_action({**payload, 'scores':normalized})

def explanation(engine, payload):
    _dict(payload, 'payload')
    normalized = _scores(payload.get('scores'), EXPLANATION_DIMS)
    return engine.build_explanation({**payload, 'scores':normalized})

def will(engine, payload):
    _dict(payload, 'payload')
    options = payload.get('options')
    if not isinstance(options, list) or not options:
        raise GateRejected('NO_OPTIONS')
    safe = []
    for option in options:
        _dict(option, 'option')
        safe.append({**option, 'scores':_scores(option.get('scores'), PURPOSE_DIMS)})
    weights = payload.get('weights')
    if weights is not None:
        weights = _scores(weights, PURPOSE_DIMS)
    return engine.decide({**payload, 'options':safe, **({'weights':weights} if weights is not None else {})})

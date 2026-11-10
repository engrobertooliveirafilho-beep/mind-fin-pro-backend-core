"""R277 fail-closed prevalidation for historical CognitiveImmuneSystem."""
import math
class InvalidCognitiveScore(ValueError): pass

def guarded_scan(engine, payload):
    if not isinstance(payload, dict) or set(payload) != {'score'}:
        raise InvalidCognitiveScore('INVALID_PAYLOAD')
    value = payload['score']
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidCognitiveScore('INVALID_SCORE_TYPE')
    try:
        finite = math.isfinite(value)
    except (TypeError, ValueError, OverflowError):
        raise InvalidCognitiveScore('INVALID_SCORE_VALUE') from None
    if not finite or not -1 <= value <= 1:
        raise InvalidCognitiveScore('INVALID_SCORE_RANGE')
    return engine.scan({'score': value})

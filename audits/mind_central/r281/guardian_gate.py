import math

class GuardianRejected(ValueError):
    pass

def checked_scan(guardian, *, explanation, reality, coherence, immunity):
    if not isinstance(explanation, dict) or not isinstance(reality, dict) or not isinstance(coherence, dict) or not isinstance(immunity, dict):
        raise GuardianRejected('INVALID_TELEMETRY')
    if set(explanation) != {'tags'} or set(reality) != {'certainty'} or set(coherence) != {'alerts'} or set(immunity) != {'flags'}:
        raise GuardianRejected('MISSING_OR_EXTRA_TELEMETRY')
    if not isinstance(explanation['tags'], list) or not isinstance(coherence['alerts'], list) or not isinstance(immunity['flags'], list):
        raise GuardianRejected('INVALID_FLAGS')
    if not all(isinstance(x,str) for k,v in [(1,explanation['tags']),(2,coherence['alerts']),(3,immunity['flags'])] for x in v):
        raise GuardianRejected('INVALID_FLAG_ITEM')
    c = reality['certainty']
    if isinstance(c,bool) or not isinstance(c,(int,float)) or not math.isfinite(c) or not 0 <= c <= 1:
        raise GuardianRejected('INVALID_CERTAINTY')
    result = guardian.scan()
    if not isinstance(result,dict) or not isinstance(result.get('protection_score'),(int,float)) or isinstance(result.get('protection_score'),bool) or not math.isfinite(result['protection_score']) or not 0<=result['protection_score']<=1:
        raise GuardianRejected('INVALID_RESULT')
    return result

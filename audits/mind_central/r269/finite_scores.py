"""R269: fail-closed numeric normalization for MIND cognitive engines.
Standalone isolated adapter; no production source is modified.
"""
import math

class InvalidScore(ValueError):
    pass

def finite_score(value, *, name='score'):
    """Accept numeric scores in [0,1]; reject NaN, infinity, booleans and strings."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidScore(f'{name}: NOT_NUMERIC')
    try:
        number = float(value)
    except (ValueError, OverflowError):
        raise InvalidScore(f'{name}: NOT_REPRESENTABLE') from None
    if not math.isfinite(number):
        raise InvalidScore(f'{name}: NON_FINITE')
    if not 0.0 <= number <= 1.0:
        raise InvalidScore(f'{name}: OUT_OF_RANGE')
    return number

def validate_scores(scores, dimensions):
    if not isinstance(scores, dict):
        raise InvalidScore('scores: NOT_DICT')
    if set(scores) != set(dimensions):
        raise InvalidScore('scores: DIMENSION_MISMATCH')
    return {key: finite_score(scores[key], name=key) for key in dimensions}

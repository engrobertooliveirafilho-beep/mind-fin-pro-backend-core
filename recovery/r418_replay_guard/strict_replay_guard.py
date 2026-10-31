"""R418: defensive gate for historical R388 replay; PAPER_ONLY."""
from __future__ import annotations
import math

def guarded_replay(replay_fn, path, *, expected_sha256, train_end, test_start, test_end):
    if not callable(replay_fn) or not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or any(c not in '0123456789abcdefABCDEF' for c in expected_sha256):
        return {'status':'BLOCKED','reason':'INVALID_INPUT','promotion_authorized':False,'ftmo_certified':False}
    try:
        result = replay_fn(path, expected_sha256=expected_sha256, train_end=train_end, test_start=test_start, test_end=test_end)
    except (OSError, ValueError, KeyError, TypeError, OverflowError, UnicodeError, ZeroDivisionError) as exc:
        return {'status':'BLOCKED','reason':type(exc).__name__,'promotion_authorized':False,'ftmo_certified':False}
    if not isinstance(result, dict) or result.get('status') != 'PAPER_REPLAY_ONLY' or result.get('promotion_authorized') is not False or result.get('ftmo_certified') is not False:
        return {'status':'BLOCKED','reason':'UNVERIFIED_RESULT','promotion_authorized':False,'ftmo_certified':False}
    n = result.get('signals')
    avg = result.get('mean_forward_return')
    if type(n) is not int or n <= 0 or not isinstance(avg, (int,float)) or not math.isfinite(avg):
        return {'status':'BLOCKED','reason':'EMPTY_OR_INVALID_SCORE','promotion_authorized':False,'ftmo_certified':False}
    return {**result, 'promotion_authorized':False, 'ftmo_certified':False}

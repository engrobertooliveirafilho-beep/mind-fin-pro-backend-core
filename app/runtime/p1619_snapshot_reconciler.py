"""Read-only P1619 historical candle snapshot reconciliation; no trading signals."""
import hashlib
import json
from pathlib import Path

WEIGHTS = {'doji': 0, 'hammer': 15, 'shooting_star': 15,
           'bullish_engulfing': 20, 'bearish_engulfing': 20,
           'inside_bar': 10, 'outside_bar': 10}

def reconcile(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError('missing historical snapshot')
    seen = set()
    mismatches = []
    active = 0
    for i, row in enumerate(rows):
        if not isinstance(row, dict) or not isinstance(row.get('asset'), str) or not row['asset'] or not isinstance(row.get('timeframe'), str) or not row['timeframe']:
            raise ValueError('invalid asset/timeframe')
        key = (row['asset'], row['timeframe'])
        if key in seen:
            raise ValueError('duplicate asset/timeframe')
        seen.add(key)
        for field in WEIGHTS:
            if type(row.get(field)) is not int or row[field] not in (0, 1):
                raise ValueError('invalid candle flag')
        if type(row.get('candle_score')) is not int or row['candle_score'] < 0:
            raise ValueError('invalid candle score')
        expected = sum(weight * row[field] for field, weight in WEIGHTS.items())
        if row['candle_score'] != expected:
            mismatches.append({'index': i, 'asset': row['asset'], 'timeframe': row['timeframe'], 'observed': row['candle_score'], 'expected': expected})
        active += bool(row['candle_score'])
    return {'status': 'RECONCILED' if not mismatches else 'SCORE_MISMATCH', 'rows': len(rows), 'active_scores': active,
            'mismatches': mismatches, 'order_send_allowed': False, 'promotion_allowed': False, 'e2e_certified': False}

def reconcile_file(path):
    raw = Path(path).read_bytes()
    result = reconcile(json.loads(raw))
    result['historical_sha256'] = hashlib.sha256(raw).hexdigest()
    return result

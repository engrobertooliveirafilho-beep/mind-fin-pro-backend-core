"""Offline S20 symbol-lineage gate; no historical ledger mutation."""
import hashlib
import json
import re
from datetime import datetime, timezone

REQUIRED = ('day', 'tick', 'symbol', 'timestamp_utc', 'source_dataset_id', 'source_row_hash')

def validate_decision(row):
    if not isinstance(row, dict):
        raise ValueError('decision must be a dict')
    missing = [key for key in REQUIRED if not isinstance(row.get(key), str) or not row[key].strip()]
    if missing:
        raise ValueError('missing lineage: ' + ','.join(missing))
    if row.get('mode') != 'PAPER_ONLY' or row.get('real_execution_allowed') is not False:
        raise ValueError('PAPER governance violation')
    if row['symbol'] != row['symbol'].strip() or any(c.isspace() for c in row['symbol']):
        raise ValueError('invalid symbol')
    if not re.fullmatch(r'[A-Za-z0-9._/-]{1,40}', row['symbol']):
        raise ValueError('invalid symbol format')
    if not re.fullmatch(r'[0-9a-fA-F]{64}', row['source_row_hash']):
        raise ValueError('invalid source SHA256')
    if not re.fullmatch(r'[0-9]+', row['tick']):
        raise ValueError('invalid tick')
    try:
        dt = datetime.fromisoformat(row['timestamp_utc'].replace('Z', '+00:00'))
        if dt.tzinfo is None or dt.utcoffset() != timezone.utc.utcoffset(dt):
            raise ValueError()
        if dt.date().isoformat() != row['day']:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValueError('invalid UTC timestamp or day') from None
    return dict(row)

def append_immutable(rows, new_row):
    if not isinstance(rows, (tuple, list)):
        raise ValueError('invalid ledger')
    previous = [validate_decision(x) for x in rows]
    candidate = validate_decision(new_row)
    key = (candidate['day'], candidate['tick'], candidate['symbol'])
    if any((r['day'], r['tick'], r['symbol']) == key for r in previous):
        raise ValueError('duplicate decision key')
    return tuple(previous + [candidate])

def digest(rows):
    checked = [validate_decision(x) for x in rows]
    return hashlib.sha256(json.dumps(checked, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()

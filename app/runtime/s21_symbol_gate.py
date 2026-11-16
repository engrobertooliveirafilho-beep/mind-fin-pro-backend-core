"""Fail-closed S21 PAPER decision admission; no broker or order side effects."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone

class S21Blocked(ValueError):
    pass

def _sha(value: object) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdefABCDEF' for c in value):
        raise S21Blocked('INVALID_SHA256')
    return value.lower()

def admit_paper_decision(record: dict, *, source_bytes: bytes, source_sha256: str) -> dict:
    """Validate lineage and return an immutable-by-copy PAPER envelope; never guess a symbol."""
    if not isinstance(record, dict) or not isinstance(source_bytes, bytes):
        raise S21Blocked('INVALID_INPUT')
    if hashlib.sha256(source_bytes).hexdigest() != _sha(source_sha256):
        raise S21Blocked('SOURCE_HASH_MISMATCH')
    if record.get('mode') != 'PAPER_ONLY' or record.get('real_orders_allowed') is not False:
        raise S21Blocked('PAPER_ONLY_REQUIRED')
    symbol = record.get('symbol')
    if not isinstance(symbol, str) or not symbol.strip():
        raise S21Blocked('MISSING_SYMBOL')
    symbol = symbol.strip().upper()
    if not all(c.isascii() and (c.isalnum() or c in '._-') for c in symbol):
        raise S21Blocked('INVALID_SYMBOL')
    asset = record.get('asset')
    if asset is not None and (not isinstance(asset, str) or asset.strip().upper() != symbol):
        raise S21Blocked('ASSET_SYMBOL_CONFLICT')
    dataset = record.get('source_dataset_id')
    if not isinstance(dataset, str) or not dataset.strip():
        raise S21Blocked('MISSING_DATASET_ID')
    row_hash = _sha(record.get('source_row_hash'))
    try:
        dt = datetime.fromisoformat(record['timestamp_utc'].replace('Z', '+00:00'))
    except (KeyError, AttributeError, ValueError, TypeError) as exc:
        raise S21Blocked('INVALID_TIMESTAMP') from exc
    if dt.tzinfo is None or dt.utcoffset() != timezone.utc.utcoffset(dt):
        raise S21Blocked('UTC_REQUIRED')
    if record.get('day') != dt.date().isoformat():
        raise S21Blocked('DAY_TIMESTAMP_MISMATCH')
    if type(record.get('tick')) is not int or record['tick'] < 0:
        raise S21Blocked('INVALID_TICK')
    if record.get('decision_direction') not in ('BUY', 'SELL', 'HOLD'):
        raise S21Blocked('INVALID_DIRECTION')
    result = {
        'schema_version': 's21_paper_admission_v1',
        'day': record['day'], 'tick': record['tick'],
        'timestamp_utc': dt.isoformat().replace('+00:00', 'Z'),
        'symbol': symbol, 'decision_direction': record['decision_direction'],
        'source_dataset_id': dataset.strip(), 'source_row_hash': row_hash,
        'source_dataset_sha256': _sha(source_sha256),
        'mode': 'PAPER_ONLY', 'real_orders_allowed': False,
    }
    result['payload_sha256'] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
    return result

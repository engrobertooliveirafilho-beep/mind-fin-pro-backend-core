"""Offline, fail-closed S20/S21 causal join gate. No broker/network imports."""
import csv
import hashlib
import json
from pathlib import Path

REQUIRED = {'decision_id', 'strategy_id', 'symbol', 'decision_ts', 'signal_ts', 'price_ts', 'price', 'source_sha256'}

def validate(rows):
    seen = set()
    last = {}
    result = []
    for index, row in enumerate(rows, 1):
        if not REQUIRED.issubset(row):
            raise ValueError('missing_columns')
        if not all(isinstance(row[k], str) and row[k] and row[k] == row[k].strip() for k in REQUIRED):
            raise ValueError(f'blank_field:{index}')
        if row['decision_id'] in seen:
            raise ValueError('duplicate_decision')
        seen.add(row['decision_id'])
        symbol = row['symbol'].strip().upper()
        if symbol != row['symbol']:
            raise ValueError('noncanonical_symbol')
        try:
            d, s, p = (int(row[k]) for k in ('decision_ts', 'signal_ts', 'price_ts'))
            price = float(row['price'])
        except (TypeError, ValueError, OverflowError):
            raise ValueError('invalid_numeric')
        if not (0 < d <= s <= p and price > 0 and price < float('inf')):
            raise ValueError('causality_or_price')
        if symbol in last and d < last[symbol]:
            raise ValueError('nonmonotonic_decision')
        last[symbol] = d
        sha = row['source_sha256']
        if sha != sha.lower():
            raise ValueError('noncanonical_provenance_hash')
        if len(sha) != 64 or any(c not in '0123456789abcdef' for c in sha):
            raise ValueError('invalid_provenance_hash')
        result.append({'decision_id': row['decision_id'], 'symbol': symbol, 'decision_ts': d, 'signal_ts': s, 'price_ts': p})
    if not result:
        raise ValueError('empty_input')
    return {'status': 'STRUCTURAL_ONLY_NOT_OOS_CERTIFIED', 'rows': len(result), 'validated': result}

def validate_file(path, expected_sha256):
    path = Path(path)
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or any(c not in '0123456789abcdef' for c in expected_sha256):
        raise ValueError('expected_sha256_required')
    actual_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual_sha256 != expected_sha256:
        raise ValueError('snapshot_sha256_mismatch')
    with path.open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError('duplicate_or_missing_header')
        if set(reader.fieldnames) != REQUIRED:
            raise ValueError('unexpected_header')
        rows = list(reader)
        if any(None in row for row in rows):
            raise ValueError('extra_csv_columns')
    result = validate(rows)
    result['input_sha256'] = actual_sha256
    return result

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('csv_path')
    p.add_argument('--expected-sha256', required=True)
    a = p.parse_args()
    try:
        print(json.dumps(validate_file(a.csv_path, a.expected_sha256), sort_keys=True))
    except (ValueError, OSError) as e:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(e)}, sort_keys=True))
        raise SystemExit(2)

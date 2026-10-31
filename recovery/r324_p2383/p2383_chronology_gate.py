"""Read-only fail-closed validation of historical P2383 window aggregates."""
import csv
from datetime import datetime
from pathlib import Path

FMT = '%Y.%m.%d %H:%M:%S'

def inspect(path):
    rows = list(csv.DictReader(Path(path).open(newline='', encoding='utf-8-sig')))
    issues = []
    previous_end = None
    for row in rows:
        ident = row['window_id']
        try:
            start = datetime.strptime(row['start_time'], FMT)
            end = datetime.strptime(row['end_time'], FMT)
        except (ValueError, KeyError) as exc:
            issues.append(f'window {ident}: invalid timestamp: {exc}')
            continue
        if start > end:
            issues.append(f'window {ident}: start after end')
        if previous_end is not None and start <= previous_end:
            issues.append(f'window {ident}: not strictly after prior window end')
        previous_end = end
    return issues

def certify(path):
    issues = inspect(path)
    if issues:
        raise ValueError('P2383_CHRONOLOGY_BLOCKED: ' + '; '.join(issues))
    return True

"""Read-only, fail-closed bridge for historical P203–P400 promoted edges.

Produces PAPER selection candidates only; never places orders or certifies edges.
"""
import json
import math
from pathlib import Path

BLOCKS = {'LIVE':'FORBIDDEN','REAL_BROKER':'DISABLED','REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN'}


def load_candidates(path, *, limit=300):
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1 or limit > 6435:
        raise ValueError('invalid selection limit')
    records = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(records, list) or not records:
        raise ValueError('missing promoted edge records')
    candidates = []
    seen = set()
    for record in records:
        if not isinstance(record, dict) or any(record.get(k) != v for k,v in BLOCKS.items()):
            raise ValueError('unsafe or malformed edge')
        if record.get('approved_backtest') is not True or record.get('walk_forward_status') != 'APPROVED' or record.get('monte_carlo_status') != 'APPROVED':
            raise ValueError('edge lacks historical approval flags')
        job = record.get('job_id')
        score = record.get('score')
        if not isinstance(job,str) or not job or job in seen or not isinstance(score,(int,float)) or isinstance(score,bool) or not math.isfinite(score):
            raise ValueError('invalid/duplicate edge identifier or score')
        seen.add(job)
        candidates.append(record)
    return sorted(candidates, key=lambda r:(-r['score'],r['job_id']))[:limit]

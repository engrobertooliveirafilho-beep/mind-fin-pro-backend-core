import json
import os
from pathlib import Path

import pytest

from app.runtime.p401_source_bridge import load_candidates

BLOCKS = {'LIVE':'FORBIDDEN','REAL_BROKER':'DISABLED','REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN'}


def edge(job='a', score=1.5):
    return dict(job_id=job,score=score,approved_backtest=True,
                walk_forward_status='APPROVED',monte_carlo_status='APPROVED',**BLOCKS)


def write(tmp_path, records):
    path=tmp_path/'promoted.json'
    path.write_text(json.dumps(records),encoding='utf-8')
    return path


def test_ranked_candidates(tmp_path):
    result=load_candidates(write(tmp_path,[edge('b',1.0),edge('a',2.0)]))
    assert [r['job_id'] for r in result]==['a','b']


def test_reject_real_order(tmp_path):
    item=edge()
    item['REAL_ORDERS']='ALLOWED'
    with pytest.raises(ValueError):load_candidates(write(tmp_path,[item]))


def test_reject_missing_approval(tmp_path):
    item=edge()
    item['monte_carlo_status']='REJECTED'
    with pytest.raises(ValueError):load_candidates(write(tmp_path,[item]))


def test_reject_duplicate(tmp_path):
    with pytest.raises(ValueError):load_candidates(write(tmp_path,[edge(),edge()]))


def test_reject_invalid_score(tmp_path):
    with pytest.raises(ValueError):load_candidates(write(tmp_path,[edge(score=float('nan'))]))


def test_reject_empty(tmp_path):
    with pytest.raises(ValueError):load_candidates(write(tmp_path,[]))


def test_reject_invalid_limit(tmp_path):
    with pytest.raises(ValueError):load_candidates(write(tmp_path,[edge()]),limit=0)


def test_historical_source_when_available():
    source=os.getenv('ELDORA_PROMOTED_SOURCE')
    if not source:
        pytest.skip('Set ELDORA_PROMOTED_SOURCE to original read-only P361-P390 JSON')
    assert len(load_candidates(Path(source),limit=6435))==6435

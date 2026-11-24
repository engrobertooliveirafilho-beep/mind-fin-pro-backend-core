import hashlib
from pathlib import Path
from p2279e_robustness_walkforward import read_rows, freeze_development, evaluate_frozen_holdout
from mind_trader.app.validation.walk_forward_authority import walk_forward_authority

def test_real_authority():
    rows=read_rows(Path(__file__).with_name('AUDUSD_D1.csv'))
    assert len(rows)==717
    commitment=freeze_development(rows[:len(rows)//2],'SMA','2,5',round_trip_cost=.0002)
    result=evaluate_frozen_holdout(rows,commitment,expected_sha256=hashlib.sha256(commitment.encode()).hexdigest())
    assert len(result['windows'])==4 and all(w is not None for w in result['windows'])
    assert sum(w['trades'] for w in result['windows'])==82
    assert walk_forward_authority(result['windows'])['passed'] is False
    assert result['passed'] is False and result['production']=='BLOCKED'

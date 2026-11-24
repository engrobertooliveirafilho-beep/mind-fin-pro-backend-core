import hashlib
from pathlib import Path
from p2279e_robustness_walkforward import read_rows, freeze_development, evaluate_frozen_holdout
from mind_trader.app.validation.walk_forward_authority import walk_forward_authority

def test_real_authority():
    dataset=Path(__file__).with_name('AUDUSD_D1.csv')
    assert hashlib.sha256(dataset.read_bytes()).hexdigest() == '5275a6986eec9cc7ae0104fbce73e3870281fac018142ddb63cfcf20b34196e7'
    rows=read_rows(dataset)
    assert len(rows)==717
    commitment=freeze_development(rows[:len(rows)//2],'SMA','2,5',round_trip_cost=.0002)
    result=evaluate_frozen_holdout(rows,commitment,expected_sha256=hashlib.sha256(commitment.encode()).hexdigest())
    assert len(result['windows'])==4 and all(w is not None for w in result['windows'])
    assert sum(w['trades'] for w in result['windows'])==82
    assert walk_forward_authority(result['windows'])['passed'] is False
    assert result['passed'] is False and result['production']=='BLOCKED'

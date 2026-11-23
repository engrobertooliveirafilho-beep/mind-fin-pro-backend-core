from app.runtime.p2396_unique_member_quorum_r60 import validate_unique_quorum as check

def vote(member='a', allowed=True):
    return dict(member_id=member,mode='PAPER_ONLY',real_orders='FORBIDDEN',ftmo_real='FORBIDDEN',allowed=allowed,edge_score_decision='PROMOTE_SCORE',route='PAPER_OPERATIONAL')

def test_duplicate(): assert check([vote(),vote()]) == (False,'DUPLICATE_MEMBER')
def test_distinct_unverified(): assert check([vote('a'),vote('b')]) == (False,'INDEPENDENT_ENSEMBLE_EVIDENCE_REQUIRED')
def test_one(): assert check([vote()]) == (False,'INSUFFICIENT_OPERATIONAL_QUORUM')
def test_real(): assert check([dict(vote(),real_orders='ALLOWED')]) == (False,'EXECUTION_MODE_FORBIDDEN')
def test_missing_identity(): assert check([dict(vote(),member_id='')]) == (False,'MEMBER_ID_REQUIRED')

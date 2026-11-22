import pytest
from app.runtime.p2315_filebridge_offline import parse_paper_signal,reconcile_clear
SIGNAL="GER40,BUY,0.01,P2311_ACTIVE_TEST,2026-06-22T14:27:15"

def test_historical_manual_clear_not_a_receipt():
    r=reconcile_clear(SIGNAL,after_exists=False,backup_content=SIGNAL)
    assert r["backup_preserved"] and not r["terminal_read_proven"]
    assert r["orders_authorized"]==0

@pytest.mark.parametrize("signal",[
    "EURUSD,BUY,0.01,P2311_ACTIVE_TEST,2026-06-22T14:27:15",
    "GER40,HOLD,0.01,P2311_ACTIVE_TEST,2026-06-22T14:27:15",
    "GER40,BUY,1,P2311_ACTIVE_TEST,2026-06-22T14:27:15",
    "GER40,BUY,NaN,P2311_ACTIVE_TEST,2026-06-22T14:27:15",
    "GER40,BUY,0.01,UNKNOWN,2026-06-22T14:27:15",
    "GER40,BUY,0.01,P2311_ACTIVE_TEST,INVALID",
    "GER40,BUY,0.01,P2311_ACTIVE_TEST",
])
def test_reject_invalid_signal(signal):
    with pytest.raises(ValueError):parse_paper_signal(signal)

@pytest.mark.parametrize("exists,backup",[(True,SIGNAL),(False,"WRONG")])
def test_cannot_claim_clear_without_matching_backup(exists,backup):
    with pytest.raises(ValueError):reconcile_clear(SIGNAL,after_exists=exists,backup_content=backup)

def test_original_p2316_fresh_signal_parses_without_authorizing_order():
    content="GER40,BUY,0.01,P2316_34f0bb1186de,2026-06-22T14:47:30"
    signal=parse_paper_signal(content)
    assert signal.signal_id=="P2316_34f0bb1186de"
    assert signal.symbol=="GER40"

@pytest.mark.parametrize("bad_id",["P2316_", "P2316_34f0bb1186dg", "P2317_34f0bb1186de", "P2316_34f0bb1186de_EXTRA"])
def test_unverified_signal_ids_rejected(bad_id):
    with pytest.raises(ValueError):
        parse_paper_signal(f"GER40,BUY,0.01,{bad_id},2026-06-22T14:47:30")

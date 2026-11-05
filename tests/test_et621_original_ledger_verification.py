import hashlib
import pytest
from app.runtime.et621_original_ledger_verification import LedgerBlocked, verify_original_csv, convert_points_to_account_currency

RAW = b"trade_id,edge_id,pnl\nT1,E,10\nT2,E,-4\n"
SHA = hashlib.sha256(RAW).hexdigest()

def verified():
    return verify_original_csv(RAW, SHA, edge_id="E")

def test_exact_bytes():
    assert verified()["sha256"] == SHA

def test_mutation_blocks():
    with pytest.raises(LedgerBlocked):
        verify_original_csv(RAW+b"\n", SHA, edge_id="E")

def test_wrong_edge_blocks():
    with pytest.raises(LedgerBlocked):
        verify_original_csv(RAW, SHA, edge_id="OTHER")

def test_missing_original_blocks():
    with pytest.raises(LedgerBlocked):
        verify_original_csv(b"", SHA, edge_id="E")

def test_conversion():
    result = convert_points_to_account_currency(verified(), symbol="DE40", volume_lots="0.5", money_per_point_per_lot="2", contract_source_sha256="a"*64, account_currency="EUR", source_currency="EUR")
    assert [x["pnl"] for x in result] == ["10.0", "-4.0"]

def test_currency_mismatch_blocks():
    with pytest.raises(LedgerBlocked):
        convert_points_to_account_currency(verified(), symbol="DE40", volume_lots="1", money_per_point_per_lot="2", contract_source_sha256="a"*64, account_currency="USD", source_currency="EUR")

def test_missing_contract_blocks():
    with pytest.raises(LedgerBlocked):
        convert_points_to_account_currency(verified(), symbol="DE40", volume_lots="1", money_per_point_per_lot="2", contract_source_sha256="", account_currency="EUR", source_currency="EUR")

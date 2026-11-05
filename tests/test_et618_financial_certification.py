from app.runtime.et618_financial_certification import validate_financial_evidence
from app.runtime.et618_financial_validation import CertificationBlocked
import pytest

def test_missing_ledger_rejected():
    with pytest.raises(CertificationBlocked):
        validate_financial_evidence([], {}, {})

def test_no_source_rejected():
    with pytest.raises(CertificationBlocked):
        validate_financial_evidence([{"trade_id": "1"}], {"source_verified": False}, {})

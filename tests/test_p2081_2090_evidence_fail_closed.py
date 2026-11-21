import pytest
from app.runtime.p2081_2090_realtime_portfolio_governance import (
    extract_specialists, extract_runtime_metrics
)

def test_missing_real_dna_portfolio_is_rejected():
    with pytest.raises(ValueError, match="REALDNA_SPECIALISTS_MISSING_OR_EMPTY"):
        extract_specialists({})

def test_duplicate_real_dna_ids_are_rejected():
    with pytest.raises(ValueError, match="REALDNA_SPECIALIST_ID_DUPLICATE"):
        extract_specialists([{"id":"A"},{"id":"A"}])

def test_incomplete_runtime_metrics_are_rejected():
    with pytest.raises(ValueError, match="P2071_RUNTIME_METRICS_INCOMPLETE"):
        extract_runtime_metrics({"metrics":{"cycles":1200}})

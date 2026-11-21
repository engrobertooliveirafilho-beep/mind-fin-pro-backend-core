import pytest
from app.runtime.p2067_allocation_contract import reconcile_p2067_weights


HISTORICAL = [
    {"specialist_id": "XAUUSD_M1_REALDNA_0004", "normalized_weight": 0.5},
    {"specialist_id": "XAUUSD_M1_REALDNA_0003", "normalized_weight": 0.249856},
    {"specialist_id": "XAUUSD_M1_REALDNA_0001", "normalized_weight": 0.164287},
]


def test_historical_p2067_unallocated_weight_fails_closed():
    with pytest.raises(ValueError, match="P2067_UNDECLARED_RESIDUAL"):
        reconcile_p2067_weights(HISTORICAL)


def test_explicit_matching_reserve_is_allowed_only_if_declared():
    assert reconcile_p2067_weights(HISTORICAL, declared_reserve="0.085857") == {
        "allocated": "0.914143", "reserve": "0.085857", "specialists": 3
    }


@pytest.mark.parametrize("reserve", ["0", "0.08", "-0.01", "NaN"])
def test_incorrect_reserve_rejected(reserve):
    with pytest.raises(ValueError):
        reconcile_p2067_weights(HISTORICAL, declared_reserve=reserve)


def test_overallocated_portfolio_rejected():
    with pytest.raises(ValueError, match="P2067_OVERALLOCATED"):
        reconcile_p2067_weights([{"specialist_id": "A", "normalized_weight": 0.8}, {"specialist_id": "B", "normalized_weight": 0.4}])


def test_duplicate_specialist_rejected():
    with pytest.raises(ValueError, match="P2067_INVALID_SPECIALIST"):
        reconcile_p2067_weights([{"specialist_id": "A", "normalized_weight": 0.5}, {"specialist_id": "A", "normalized_weight": 0.5}])

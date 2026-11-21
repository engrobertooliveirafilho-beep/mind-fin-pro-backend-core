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

def test_portfolio_loader_rejects_historical_undeclared_residual(tmp_path):
    import json
    from app.runtime.p2071_2080_realtime_paper_runtime import load_portfolio
    path = tmp_path / "portfolio.json"
    path.write_text(json.dumps({"specialists": [
        {"specialist_id": row["specialist_id"], "logic_type": "RANGE_REVERSION",
         "normalized_weight": row["normalized_weight"]} for row in HISTORICAL
    ]}), encoding="utf-8")
    with pytest.raises(ValueError, match="P2067_UNDECLARED_RESIDUAL"):
        load_portfolio(str(path))


def test_portfolio_loader_accepts_explicit_reserve(tmp_path):
    import json
    from app.runtime.p2071_2080_realtime_paper_runtime import load_portfolio
    path = tmp_path / "portfolio.json"
    path.write_text(json.dumps({"declared_reserve": "0.085857", "specialists": [
        {"specialist_id": row["specialist_id"], "logic_type": "RANGE_REVERSION",
         "normalized_weight": row["normalized_weight"]} for row in HISTORICAL
    ]}), encoding="utf-8")
    assert len(load_portfolio(str(path))) == 3


def test_portfolio_loader_rejects_partial_weights(tmp_path):
    import json
    from app.runtime.p2071_2080_realtime_paper_runtime import load_portfolio
    path = tmp_path / "portfolio.json"
    path.write_text(json.dumps({"specialists": [
        {"specialist_id": "A", "logic_type": "RANGE_REVERSION", "normalized_weight": 0.5},
        {"specialist_id": "B", "logic_type": "RANGE_REVERSION"},
    ]}), encoding="utf-8")
    with pytest.raises(ValueError, match="P2067_PARTIAL_ALLOCATION"):
        load_portfolio(str(path))

def test_allocation_accepts_id_alias():
    rows = [{"id": "A", "normalized_weight": 1.0}]
    assert reconcile_p2067_weights(rows)["specialists"] == 1


def test_conflicting_id_aliases_fail_closed():
    rows = [{"id": "A", "specialist_id": "B", "normalized_weight": 1.0}]
    with pytest.raises(ValueError, match="P2067_CONFLICTING_SPECIALIST_ID"):
        reconcile_p2067_weights(rows)


def test_loader_rejects_reserve_without_weights(tmp_path):
    import json
    from app.runtime.p2071_2080_realtime_paper_runtime import load_portfolio
    path = tmp_path / "portfolio.json"
    path.write_text(json.dumps({"declared_reserve": 0.1, "specialists": [
        {"id": "A", "logic_type": "RANGE_REVERSION"},
    ]}), encoding="utf-8")
    with pytest.raises(ValueError, match="P2067_RESERVE_WITHOUT_WEIGHTS"):
        load_portfolio(str(path))

def test_loader_rejects_conflicting_specialist_identity_without_weights(tmp_path):
    import json
    from app.runtime.p2071_2080_realtime_paper_runtime import load_portfolio
    path = tmp_path / "portfolio.json"
    path.write_text(json.dumps({"specialists": [
        {"id": "A", "specialist_id": "B", "logic_type": "RANGE_REVERSION"},
    ]}), encoding="utf-8")
    with pytest.raises(ValueError, match="REALDNA_SPECIALIST_ID_CONFLICT"):
        load_portfolio(str(path))

def test_loader_rejects_conflicting_strategy_aliases(tmp_path):
    import json
    from app.runtime.p2071_2080_realtime_paper_runtime import load_portfolio
    path = tmp_path / "portfolio.json"
    path.write_text(json.dumps({"specialists": [
        {"id": "A", "logic_type": "RANGE_REVERSION", "strategy_type": "MOMENTUM"},
    ]}), encoding="utf-8")
    with pytest.raises(ValueError, match="REALDNA_SPECIALIST_STRATEGY_CONFLICT"):
        load_portfolio(str(path))


def test_loader_accepts_equivalent_strategy_aliases(tmp_path):
    import json
    from app.runtime.p2071_2080_realtime_paper_runtime import load_portfolio
    path = tmp_path / "portfolio.json"
    path.write_text(json.dumps({"specialists": [
        {"id": "A", "logic_type": "range_reversion", "strategy_type": "RANGE_REVERSION"},
    ]}), encoding="utf-8")
    assert len(load_portfolio(str(path))) == 1

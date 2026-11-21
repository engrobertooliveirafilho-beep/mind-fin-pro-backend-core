import pytest
from app.runtime.p2923_robustness import (
    block_bootstrap, evaluate_candidate, regime_metrics, safety_contract,
)

PASS = {
    "walk_forward_status": "WALK_FORWARD_PASS",
    "samples_train": 60,
    "samples_validation": 30,
    "samples_test": 30,
}

def test_bootstrap_is_reproducible_and_uses_blocks():
    rs = [1.0, -0.5, 0.7, -0.2] * 10
    a = block_bootstrap(rs, runs=100, block_size=3)
    b = block_bootstrap(rs, runs=100, block_size=3)
    assert a == b
    assert a["method"] == "CIRCULAR_BLOCK_BOOTSTRAP"
    assert a["sample_count"] == 40

def test_bootstrap_rejects_nonfinite_returns():
    with pytest.raises(ValueError, match="INVALID_TRADE_RETURN"):
        block_bootstrap([1.0, float("nan")])

def test_bootstrap_rejects_invalid_block_size():
    with pytest.raises(ValueError, match="INVALID_BLOCK_SIZE"):
        block_bootstrap([1.0, -1.0], block_size=3)

def test_regime_metrics_separate_market_regimes():
    result = regime_metrics([
        {"r": 1.0, "regime": "TREND"},
        {"r": -0.5, "regime": "TREND"},
        {"r": 0.5, "regime": "RANGE"},
        {"r": 0.25, "regime": "RANGE"},
    ])
    assert result["TREND"]["samples"] == 2
    assert result["RANGE"]["expectancy_r"] == 0.375

def test_candidate_blocks_if_walk_forward_not_passed():
    result = evaluate_candidate({"walk_forward_status": "FAIL"}, [])
    assert result["status"] == "BLOCKED_WALK_FORWARD_NOT_PASSED"

def test_candidate_blocks_p2922_single_pass_low_samples():
    row = {
        "walk_forward_status": "WALK_FORWARD_PASS",
        "samples_train": 6,
        "samples_validation": 2,
        "samples_test": 2,
    }
    result = evaluate_candidate(row, [], min_samples_per_partition=30)
    assert result["status"] == "BLOCKED_LOW_SAMPLE_SIZE"
    assert result["insufficient_partitions"] == {
        "samples_train": 6, "samples_validation": 2, "samples_test": 2
    }

def test_candidate_blocks_when_raw_trade_series_is_missing():
    row = {**PASS}
    result = evaluate_candidate(row, [], min_samples_per_partition=30)
    assert result["status"] == "BLOCKED_MISSING_RAW_TRADE_SERIES"

def test_candidate_requires_multiple_regimes():
    row = {**PASS}
    trades = [{"r": 0.1, "regime": "TREND"} for _ in range(120)]
    result = evaluate_candidate(row, trades, min_samples_per_partition=30, runs=20, block_size=5)
    assert result["status"] == "BLOCKED_INSUFFICIENT_REGIME_COVERAGE"

def test_candidate_returns_review_not_auto_promotion():
    row = {**PASS}
    trades = ([{"r": 0.2, "regime": "TREND"} for _ in range(60)]
              + [{"r": -0.1, "regime": "RANGE"} for _ in range(60)])
    result = evaluate_candidate(row, trades, min_samples_per_partition=30, runs=50, block_size=5)
    assert result["status"] == "ROBUSTNESS_REVIEW_REQUIRED"
    assert result["execution_allowed"] is False
    assert result["capital_allocation"] == 0.0
    assert result["promotion_allowed"] is False

def test_safety_contract_is_fail_closed():
    contract = safety_contract()
    assert contract["execution_allowed"] is False
    assert contract["capital_allocation"] == 0.0
    assert contract["promotion_allowed"] is False

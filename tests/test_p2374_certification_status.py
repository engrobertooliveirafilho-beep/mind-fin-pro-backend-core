import importlib.util
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "app"
    / "runtime"
    / "p2374_de40_observed_candidate_deep_walk_forward.py"
)
SPEC = importlib.util.spec_from_file_location("p2374_runner", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_zero_promotions_are_not_reported_as_certified():
    result = MODULE.certification_outcome(0)
    assert result["status"] == "EXECUTION_COMPLETE"
    assert result["strategy_certification"] == "NOT_GRANTED"
    assert result["promotion_outcome"] == "NO_CANDIDATE_PROMOTED"
    assert "NOT_STRATEGY_CERTIFICATION" in result["certification"]


def test_promoted_candidate_remains_paper_only_and_uncertified():
    result = MODULE.certification_outcome(1)
    assert result["status"] == "EXECUTION_COMPLETE"
    assert result["strategy_certification"] == "NOT_GRANTED"
    assert result["promotion_outcome"] == "PAPER_CANDIDATES_AVAILABLE"


def test_negative_promotion_count_fails_closed():
    try:
        MODULE.certification_outcome(-1)
    except ValueError:
        return
    raise AssertionError("negative promotion count must be rejected")

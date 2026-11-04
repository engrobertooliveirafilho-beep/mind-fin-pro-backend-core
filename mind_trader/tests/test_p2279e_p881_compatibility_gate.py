"""P2279E compatibility gate against EXISTING P8.81 authority.

No new backtest engine, no broker, no live orders. The historical P2279E
approval is retrospective and MUST NOT be promoted as P8.81 approval.
"""
from mind_trader.app.validation.walk_forward_authority import walk_forward_authority


def test_p2279e_historical_approval_is_not_p881_authority():
    # The historical P2279E accepted 2/4 positive windows, unlike P8.81.
    windows = [
        {"expectancy": 1.0, "profit_factor": 1.2},
        {"expectancy": 1.0, "profit_factor": 1.2},
        {"expectancy": -1.0, "profit_factor": 0.8},
        {"expectancy": -1.0, "profit_factor": 0.8},
    ]
    decision = walk_forward_authority(windows)
    assert decision["passed"] is False
    assert decision["production"] == "BLOCKED"
    assert decision["live"] == "FORBIDDEN"
    assert decision["edge_claim"] == "NONE"


def test_p881_rejects_historical_summary_without_window_evidence():
    # P2279E's 11/12 summary alone is not sufficient for the existing gate.
    decision = walk_forward_authority([])
    assert decision["passed"] is False
    assert decision["decision"] == "WALK_FORWARD_INSUFFICIENT_WINDOWS"
    assert decision["production"] == "BLOCKED"


def test_p881_pass_is_research_only():
    windows = [
        {"expectancy": 1.0, "profit_factor": 1.3},
        {"expectancy": 0.5, "profit_factor": 1.2},
        {"expectancy": 0.2, "profit_factor": 1.1},
    ]
    decision = walk_forward_authority(windows)
    assert decision["passed"] is True
    assert decision["decision"] == "WALK_FORWARD_PASS_RESEARCH_ONLY"
    assert decision["production"] == "BLOCKED"
    assert decision["edge_claim"] == "NONE"

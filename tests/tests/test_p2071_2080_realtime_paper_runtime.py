import os
import json
from pathlib import Path

from app.runtime.p2071_2080_realtime_paper_runtime import (
    enforce_paper_only,
    assert_no_financial_execution,
    run_p2071_2080,
)


def test_absolute_locks():
    locks = enforce_paper_only()
    assert locks["MIND_MODE"] == "PAPER_ONLY"
    assert locks["REAL_ORDERS"] == "FORBIDDEN"
    assert locks["LIVE_TRADING"] == "FALSE"
    assert locks["BROKER_EXECUTION"] == "DISABLED"
    assert locks["FINANCIAL_EXECUTION"] == "DISABLED"
    assert locks["FTMO_REAL"] == "FORBIDDEN"
    assert locks["SEND_ORDER"] == "BLOCKED"
    assert locks["MT5_ORDER_SEND"] == "BLOCKED"
    assert locks["BROKER_API_CALL"] == "BLOCKED"
    assert_no_financial_execution()


def test_p2071_2080_runtime_certification(tmp_path):
    portfolio_path = Path("data/specialists/P2066_2070/PORTFOLIO_FINAL_LOCKED_REALDNA.json")
    assert portfolio_path.exists()

    result = run_p2071_2080(
        portfolio_path=str(portfolio_path),
        output_dir=str(tmp_path),
        cycles=1200,
    )

    assert result["status"] == "PASS"
    assert result["readiness"] == "REALTIME_PAPER_RUNTIME_CERTIFIED"
    assert result["absolute_restrictions"]["REAL_ORDERS"] == "FORBIDDEN"
    assert result["absolute_restrictions"]["BROKER_EXECUTION"] == "DISABLED"
    assert result["absolute_restrictions"]["FINANCIAL_EXECUTION"] == "DISABLED"
    assert result["metrics"]["cycles"] == 1200
    assert result["metrics"]["frames_built"] == 1200
    assert Path(result["evidence_files"]["final_json"]).exists()
    assert Path(result["evidence_files"]["audit"]).exists()

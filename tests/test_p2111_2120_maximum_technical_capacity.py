from pathlib import Path

from app.runtime.p2111_2120_maximum_technical_capacity import (
    enforce_paper_only,
    assert_no_financial_execution,
    run_p2111_2120,
)


def test_p2111_2120_locks():
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


def test_p2111_2120_max_capacity_certification(tmp_path):
    result = run_p2111_2120(
        repo=".",
        portfolio_path="data/specialists/P2066_2070/PORTFOLIO_FINAL_LOCKED_REALDNA.json",
        p2071_certification_path="data/runtime/P2071_2080/evidence/P2071_2080_FINAL_CERTIFICATION.json",
        p2081_certification_path="data/runtime/P2081_2090/evidence/P2081_2090_FINAL_CERTIFICATION.json",
        p2091_certification_path="data/runtime/P2091_2100/evidence/P2091_2100_FINAL_CERTIFICATION.json",
        p2101_certification_path="data/runtime/P2101_2110/evidence/P2101_2110_FINAL_CERTIFICATION.json",
        output_dir=str(tmp_path),
    )

    assert result["status"] == "PASS"
    assert result["readiness"] == "MAXIMUM_TECHNICAL_CAPACITY_CERTIFIED"
    assert result["mission_status"]["P2120_MAXIMUM_CAPACITY_CERTIFICATION"] == "PASS"
    assert result["final_state"]["known_critical_gaps"] == 0
    assert result["absolute_restrictions"]["REAL_ORDERS"] == "FORBIDDEN"
    assert result["absolute_restrictions"]["BROKER_EXECUTION"] == "DISABLED"
    assert result["absolute_restrictions"]["FINANCIAL_EXECUTION"] == "DISABLED"

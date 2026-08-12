from pathlib import Path

from app.runtime.p2101_2110_autonomous_paper_operations import (
    enforce_paper_only,
    assert_no_financial_execution,
    run_p2101_2110,
)


def test_p2101_2110_locks():
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


def test_p2101_2110_autonomous_certification(tmp_path):
    portfolio = Path("data/specialists/P2066_2070/PORTFOLIO_FINAL_LOCKED_REALDNA.json")
    p2071 = Path("data/runtime/P2071_2080/evidence/P2071_2080_FINAL_CERTIFICATION.json")
    p2081 = Path("data/runtime/P2081_2090/evidence/P2081_2090_FINAL_CERTIFICATION.json")
    p2091 = Path("data/runtime/P2091_2100/evidence/P2091_2100_FINAL_CERTIFICATION.json")

    assert portfolio.exists()
    assert p2071.exists()
    assert p2081.exists()
    assert p2091.exists()

    result = run_p2101_2110(
        portfolio_path=str(portfolio),
        p2071_certification_path=str(p2071),
        p2081_certification_path=str(p2081),
        p2091_certification_path=str(p2091),
        output_dir=str(tmp_path),
    )

    assert result["status"] == "PASS"
    assert result["readiness"] == "AUTONOMOUS_PAPER_OPERATIONS_CERTIFIED"
    assert result["mission_status"]["P2110_AUTONOMOUS_CERTIFICATION"] == "PASS"
    assert result["absolute_restrictions"]["REAL_ORDERS"] == "FORBIDDEN"
    assert result["absolute_restrictions"]["BROKER_EXECUTION"] == "DISABLED"
    assert result["absolute_restrictions"]["FINANCIAL_EXECUTION"] == "DISABLED"
    assert result["autonomous_state"]["mode"] == "PAPER_ONLY"

import json
from pathlib import Path

from app.runtime.p2071_2080_realtime_paper_runtime import run_p2071_2080


def test_p2071_2080b_certification_and_drawdown_repair(tmp_path):
    portfolio_path = Path("data/specialists/P2066_2070/PORTFOLIO_FINAL_LOCKED_REALDNA.json")
    assert portfolio_path.exists()

    result = run_p2071_2080(
        portfolio_path=str(portfolio_path),
        output_dir=str(tmp_path),
        cycles=1200,
    )

    assert result["status"] == "PASS"
    assert result["readiness"] == "REALTIME_PAPER_RUNTIME_CERTIFIED"
    assert result["mission_status"]["P2080_REALTIME_RUNTIME_CERTIFICATION"] == "PASS"
    assert result["absolute_restrictions"]["REAL_ORDERS"] == "FORBIDDEN"
    assert result["absolute_restrictions"]["BROKER_EXECUTION"] == "DISABLED"
    assert result["absolute_restrictions"]["FINANCIAL_EXECUTION"] == "DISABLED"
    assert result["metrics"]["cycles"] == 1200
    assert result["metrics"]["frames_built"] == 1200
    assert result["metrics"]["equity_points"] >= 1200
    assert result["metrics"]["peak_equity"] >= result["metrics"]["trough_equity"]
    assert Path(result["evidence_files"]["final_json"]).exists()
    assert Path(result["evidence_files"]["audit"]).exists()

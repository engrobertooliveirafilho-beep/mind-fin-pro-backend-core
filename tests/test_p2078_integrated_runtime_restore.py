import json
from app.runtime.p2071_2080_realtime_paper_runtime import run_p2071_2080, PaperPortfolioExecutor

def test_runtime_writes_restorable_paper_executor_state(tmp_path):
    portfolio = "data/specialists/P2066_2070/PORTFOLIO_FINAL_LOCKED_REALDNA.json"
    result = run_p2071_2080(portfolio, str(tmp_path), cycles=5)
    state = json.loads((tmp_path / "runtime_state.json").read_text(encoding="utf-8"))
    restored = PaperPortfolioExecutor.restore_state(state["executor_snapshot"])
    assert restored.export_state() == state["executor_snapshot"]
    assert result["mission_status"]["P2079_RUNTIME_PERSISTENCE"] == "PASS"
    assert result["mission_status"]["P2078_RECOVERY_VALIDATION"] == "PENDING"
    assert result["mission_status"]["P2080_REALTIME_RUNTIME_CERTIFICATION"] == "FAIL"

from app.runtime.p2071_2080_realtime_paper_runtime import run_p2071_2080

def test_synthetic_loop_and_equity_readback_do_not_certify_recovery_or_sessions(tmp_path):
    portfolio = "data/specialists/P2066_2070/PORTFOLIO_FINAL_LOCKED_REALDNA.json"
    result = run_p2071_2080(portfolio, str(tmp_path), cycles=5)
    steps = result["mission_status"]
    assert steps["P2077_MULTI_SESSION_RUNTIME"] == "PENDING"
    assert steps["P2078_RECOVERY_VALIDATION"] == "PENDING"
    assert steps["P2080_REALTIME_RUNTIME_CERTIFICATION"] == "FAIL"
    assert result["realtime_feed_certified"] is False

def test_readback_does_not_promote_recovery_even_after_extended_synthetic_run(tmp_path):
    portfolio = "data/specialists/P2066_2070/PORTFOLIO_FINAL_LOCKED_REALDNA.json"
    result = run_p2071_2080(portfolio, str(tmp_path), cycles=1000)
    assert result["mission_status"]["P2078_RECOVERY_VALIDATION"] == "PENDING"
    assert result["mission_status"]["P2077_MULTI_SESSION_RUNTIME"] == "PENDING"

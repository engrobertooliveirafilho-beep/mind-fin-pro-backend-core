from app.runtime.p2101_2110_autonomous_paper_operations import AutoRecovery, AutoRestart, AutoDecision, certify

def test_recovery_dictionary_rewrite_is_not_executed_recovery():
    decision = AutoRecovery().evaluate({"runtime_status": "FAULTED", "heartbeat": 0, "recovery_count": 0})
    assert decision.status == "FAIL"
    assert decision.payload["simulation_only"] is True
    assert decision.payload["recovered"]["runtime_status"] == "RECOVERED"

def test_restart_dictionary_rewrite_is_not_executed_restart():
    decision = AutoRestart().evaluate({"runtime_status": "RECOVERED", "restart_count": 0})
    assert decision.status == "FAIL"
    assert decision.payload["simulation_only"] is True
    assert decision.payload["restarted"]["runtime_status"] == "RUNNING"

def test_synthetic_recovery_blocks_autonomous_certification():
    decisions = [AutoDecision(f"P{i}_TEST", "PASS", "TEST", {}) for i in range(2101, 2110)]
    decisions[3] = AutoRecovery().evaluate({"runtime_status": "FAULTED", "heartbeat": 0, "recovery_count": 0})
    decisions[4] = AutoRestart().evaluate({"runtime_status": "RECOVERED", "restart_count": 0})
    assert certify(decisions).status == "FAIL"

from app.runtime.p2101_2110_autonomous_paper_operations import Scheduler, AutoDecision, certify

def test_scheduler_configuration_does_not_prove_execution():
    result = Scheduler().evaluate()
    assert result.status == "FAIL"
    assert result.reason == "SCHEDULER_NOT_EXECUTED"
    assert result.payload["execution_verified"] is False
    assert result.payload["runtime_tick_interval_seconds"] == 60

def test_scheduler_declaration_blocks_autonomous_certification():
    decisions = [AutoDecision(f"P{i}_TEST", "PASS", "TEST", {}) for i in range(2101, 2110)]
    decisions[0] = Scheduler().evaluate()
    assert certify(decisions).status == "FAIL"

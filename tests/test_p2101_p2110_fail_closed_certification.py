from app.runtime.p2101_2110_autonomous_paper_operations import (
    AutoHealing, AutoReporting, AutoDecision, certify
)

def _decision(component, status):
    return AutoDecision(component=component, status=status, reason="OFFLINE_TEST", payload={})

def test_healing_is_not_certified_when_only_actions_are_proposed():
    d = AutoHealing().evaluate({"runtime_heartbeat": False})
    assert d.status == "FAIL"
    assert d.payload["healing_actions"] == ["HEAL_RUNTIME_HEARTBEAT"]

def test_healing_policy_passes_only_when_diagnostics_are_clear():
    d = AutoHealing().evaluate({"runtime_heartbeat": True})
    assert d.status == "PASS"
    assert d.payload["healing_actions"] == []

def test_reporting_rejects_failed_components():
    d = AutoReporting().evaluate([_decision("P2101_SCHEDULER", "PASS"), _decision("P2103_WATCHDOG", "FAIL")])
    assert d.status == "FAIL"
    assert d.payload["fail_count"] == 1

def test_certification_rejects_empty_decision_list():
    assert certify([]).status == "FAIL"

def test_certification_rejects_missing_steps_even_if_all_present_pass():
    assert certify([_decision("P2101_SCHEDULER", "PASS")]).status == "FAIL"

def test_certification_accepts_complete_nine_step_pass_only():
    decisions = [_decision(f"P{i}_TEST", "PASS") for i in range(2101, 2110)]
    assert certify(decisions).status == "PASS"

def test_certification_rejects_duplicate_step_even_with_nine_decisions():
    decisions = [_decision(f"P{i}_TEST", "PASS") for i in range(2101, 2110)]
    decisions[-1] = _decision("P2108_DUPLICATE", "PASS")
    assert certify(decisions).status == "FAIL"

def test_certification_rejects_surplus_step_even_when_all_required_pass():
    decisions = [_decision(f"P{i}_TEST", "PASS") for i in range(2101, 2110)]
    decisions.append(_decision("P2101_SURPLUS", "PASS"))
    assert certify(decisions).status == "FAIL"

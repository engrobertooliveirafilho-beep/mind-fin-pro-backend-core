from app.runtime.p2091_2100_realtime_intelligence_layer import IntelligenceDecision, certify

def _decision(step, status="PASS"):
    return IntelligenceDecision(component=f"P{step}_TEST", status=status, reason="TEST", payload={})

def test_empty_decisions_do_not_certify():
    assert certify([]).status == "FAIL"

def test_missing_intelligence_step_does_not_certify():
    assert certify([_decision(i) for i in range(2091, 2099)]).status == "FAIL"

def test_duplicate_intelligence_step_does_not_certify():
    decisions = [_decision(i) for i in range(2091, 2100)]
    decisions[8] = _decision(2098)
    assert certify(decisions).status == "FAIL"

def test_failing_intelligence_step_does_not_certify():
    decisions = [_decision(i) for i in range(2091, 2100)]
    decisions[4].status = "FAIL"
    assert certify(decisions).status == "FAIL"

def test_complete_intelligence_steps_certify_only_in_isolation():
    decisions = [_decision(i) for i in range(2091, 2100)]
    assert certify(decisions).status == "PASS"

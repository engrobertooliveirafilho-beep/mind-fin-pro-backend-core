from app.runtime.p2081_2090_realtime_portfolio_governance import GovernanceDecision, certify_governance

def _decision(step, status="PASS"):
    return GovernanceDecision(component=f"P{step}_TEST", status=status, reason="TEST", payload={})

def test_p2090_rejects_empty():
    assert certify_governance([]).status == "FAIL"

def test_p2090_rejects_missing_step():
    assert certify_governance([_decision(i) for i in range(2081, 2089)]).status == "FAIL"

def test_p2090_rejects_duplicate_step():
    ds = [_decision(i) for i in range(2081, 2090)]
    ds[-1] = _decision(2088)
    assert certify_governance(ds).status == "FAIL"

def test_p2090_rejects_failed_step():
    ds = [_decision(i) for i in range(2081, 2090)]
    ds[0].status = "FAIL"
    assert certify_governance(ds).status == "FAIL"

def test_p2090_complete_pass_only_at_component_level():
    assert certify_governance([_decision(i) for i in range(2081, 2090)]).status == "PASS"

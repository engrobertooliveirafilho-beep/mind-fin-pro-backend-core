from app.action_governor import ActionGovernor


def test_step525_low_risk_action_is_allowed():
    gov = ActionGovernor()
    decision = gov.evaluate({"type": "send_email", "risk_hint": 0.1})
    assert decision.status == "allowed"
    assert decision.risk_score == 0.1


def test_step525_medium_risk_needs_confirmation():
    gov = ActionGovernor(block_threshold=0.8, confirm_threshold=0.5)
    decision = gov.evaluate({"type": "transfer", "risk_hint": 0.6})
    assert decision.status == "needs_confirmation"
    assert 0.5 <= decision.risk_score < 0.8


def test_step525_high_risk_is_blocked():
    gov = ActionGovernor(block_threshold=0.8, confirm_threshold=0.5)
    decision = gov.evaluate({"type": "critical_transfer", "risk_hint": 0.95})
    assert decision.status == "blocked"
    assert decision.risk_score >= 0.8


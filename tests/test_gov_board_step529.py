from app.gov_board import GovernanceBoard


def test_step529_low_risk_leads_to_approval():
    board = GovernanceBoard(personas=["legal", "risk", "ethics"])
    decision = board.deliberate({"risk_score": 0.1})
    assert decision.outcome == "approve"
    assert len(decision.opinions) == 3
    assert all(o.vote == "approve" for o in decision.opinions)


def test_step529_high_risk_leads_to_reject():
    board = GovernanceBoard(personas=["legal", "risk", "ethics"])
    decision = board.deliberate({"risk_score": 0.9})
    assert decision.outcome == "reject"
    assert all(o.vote == "reject" for o in decision.opinions)


def test_step529_mid_risk_leads_to_abstain():
    board = GovernanceBoard(personas=["legal", "risk", "ethics"])
    decision = board.deliberate({"risk_score": 0.5})
    assert decision.outcome == "abstain"
    assert all(o.vote == "abstain" for o in decision.opinions)


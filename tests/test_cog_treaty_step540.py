from app.cog_treaty import CognitiveTreatyProtocol


def test_step540_cooperation_without_prohibited_topics_is_accepted():
    proto = CognitiveTreatyProtocol()
    parties = ["mind-a", "mind-b"]
    proposal = {
        "mode": "cooperation",
        "topics": ["risk_insights", "metrics"],
        "max_data_sensitivity": 4,
    }
    result = proto.negotiate(parties, proposal)
    assert result.status == "accepted"
    assert "cooperacao" in result.reason.lower()
    assert result.agreed_terms["mode"] == "cooperation"
    assert "mind-a" in result.agreed_terms["parties"]


def test_step540_proposal_with_aggression_topic_is_rejected():
    proto = CognitiveTreatyProtocol()
    parties = ["mind-a", "mind-b"]
    proposal = {
        "mode": "cooperation",
        "topics": ["aggression", "metrics"],
    }
    result = proto.negotiate(parties, proposal)
    assert result.status == "rejected"
    assert "proibidos" in result.reason.lower()
    assert result.agreed_terms == {}


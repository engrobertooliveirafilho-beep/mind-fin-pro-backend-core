from app.p17_value_proof.review_decision_aggregation import aggregate_review_decision

def test_p17c_review_decision_aggregation():
    result = aggregate_review_decision()
    assert result["status"] == "PASS"
    assert result["value_signal"] == "POSITIVE_PROXY"
    assert result["real_review_status"] == "PENDING"
    assert result["production_decision"] == "BLOCKED_PENDING_REAL_REVIEW"
    assert result["auto_activation_allowed"] is False
    assert result["production_enabled"] is False
    assert result["runtime_modified"] is False
    assert result["real_user_sent"] is False

from app.companionship.safe_recovery_adapter import _p19p36m_h4_authoritative_advisor_guard


def test_p19p36m_h4_blocks_false_positive_zero_score_empty_hits_no_bridge():
    advisor = {
        "should_use_memory": True,
        "memory_score": 0.0,
        "memory_hits": [],
        "recommended_memories": [],
        "bridge": False,
        "reason": "OLD_FALSE_POSITIVE"
    }

    fixed = _p19p36m_h4_authoritative_advisor_guard(advisor)

    assert fixed["should_use_memory"] is False
    assert fixed["memory_score"] == 0.0
    assert fixed["memory_hits"] == []
    assert fixed["recommended_memories"] == []
    assert fixed["bridge"] is False
    assert fixed["advisor_guard_version"] == "P19P36M_H4_AUTHORITATIVE"
    assert fixed["reason"] == "P19P36M_H4_BLOCKED_NO_POSITIVE_MEMORY_EVIDENCE"


def test_p19p36m_h4_allows_positive_memory_when_score_and_bridge_exist():
    advisor = {
        "should_use_memory": False,
        "memory_score": 0.77,
        "memory_hits": [],
        "recommended_memories": ["quero emagrecer", "tenho dor no joelho"],
        "bridge": True,
    }

    fixed = _p19p36m_h4_authoritative_advisor_guard(advisor)

    assert fixed["should_use_memory"] is True
    assert fixed["memory_score"] > 0
    assert fixed["bridge"] is True
    assert fixed["recommended_memories"] == ["quero emagrecer", "tenho dor no joelho"]
    assert fixed["advisor_guard_positive_evidence"] is True

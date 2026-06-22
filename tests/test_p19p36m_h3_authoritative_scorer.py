from app.companionship.safe_recovery_adapter import score_memory_relevance

def test_h3_scorer_always_returns_bridge():
    out = score_memory_relevance(
        text="quais exercícios?",
        history=["quero emagrecer", "tenho dor no joelho", "quais exercícios?"],
        active_subject="quero emagrecer",
        active_domain="fitness",
    )
    assert out["scorer_version"] == "P19P36M_H3_AUTHORITATIVE"
    assert "domain_semantic_bridge" in out
    assert out["current_message_excluded"] is True

def test_h3_fitness_bridge_true():
    out = score_memory_relevance(
        text="quais exercícios?",
        history=["quero emagrecer", "tenho dor no joelho", "quais exercícios?"],
        active_subject="quero emagrecer",
        active_domain="fitness",
    )
    assert out["score"] >= 0.55
    assert out["domain_semantic_bridge"]["matched"] is True
    assert "joelho" in out["memory_hits"] or "emagrecer" in out["memory_hits"]

def test_h3_business_self_match_false():
    out = score_memory_relevance(
        text="como abrir empresa de software?",
        history=["como abrir empresa de software?"],
        active_subject="como abrir empresa de software",
        active_domain="business",
    )
    assert out["current_message_excluded"] is True
    assert out["score"] == 0.0
    assert out["domain_semantic_bridge"]["matched"] is False

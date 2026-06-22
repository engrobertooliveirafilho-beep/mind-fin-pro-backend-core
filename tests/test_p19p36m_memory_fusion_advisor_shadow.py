from app.companionship.safe_recovery_adapter import (
    score_memory_relevance,
    build_memory_fusion_advisor,
    collect_memory_shadow,
    attach_memory_fusion_shadow,
    attach_memory_fusion_advisor_shadow,
)

def test_memory_fusion_advisor_should_use_relevant_memory():
    ctx = {
        "p19p36k_memory_shadow": {
            "history": ["quero emagrecer", "tenho dor no joelho"]
        },
        "p19p36l_memory_fusion_shadow": score_memory_relevance(
            text="quais exercícios para joelho?",
            history=["quero emagrecer", "tenho dor no joelho"],
            active_subject="quero emagrecer",
            active_domain="fitness",
        )
    }
    advisor = build_memory_fusion_advisor(ctx)
    assert advisor["should_use_memory"] is True
    assert advisor["memory_score"] >= 0.55
    assert "joelho" in advisor["memory_hits"] or "emagrecer" in advisor["memory_hits"]

def test_memory_fusion_advisor_rejects_unrelated_memory():
    ctx = {
        "p19p36k_memory_shadow": {
            "history": ["quero emagrecer", "tenho dor no joelho"]
        },
        "p19p36l_memory_fusion_shadow": score_memory_relevance(
            text="como abrir empresa de software?",
            history=["quero emagrecer", "tenho dor no joelho"],
            active_subject="empresa de software",
            active_domain="business",
        )
    }
    advisor = build_memory_fusion_advisor(ctx)
    assert advisor["should_use_memory"] is False

def test_memory_fusion_advisor_attached_to_context():
    ctx = {"active_domain": "fitness", "active_subject": "quero emagrecer"}
    ctx = collect_memory_shadow("+551111120001", "quero emagrecer", ctx)
    ctx = collect_memory_shadow("+551111120001", "tenho dor no joelho", ctx)
    ctx = attach_memory_fusion_shadow("+551111120001", "quais exercícios?", ctx)
    ctx = attach_memory_fusion_advisor_shadow(ctx)
    assert "p19p36m_memory_fusion_advisor_shadow" in ctx
    assert "should_use_memory" in ctx["p19p36m_memory_fusion_advisor_shadow"]

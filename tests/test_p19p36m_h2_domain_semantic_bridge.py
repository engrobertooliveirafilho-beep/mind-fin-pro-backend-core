from app.companionship.safe_recovery_adapter import (
    collect_memory_shadow,
    attach_memory_fusion_shadow,
    attach_memory_fusion_advisor_shadow,
    score_memory_relevance,
)

def test_h2_fitness_bridge_recovers_exercise_question():
    hist = ["quero emagrecer", "tenho dor no joelho"]
    out = score_memory_relevance(
        text="quais exercícios?",
        history=hist,
        active_subject="quero emagrecer",
        active_domain="fitness",
    )
    assert out["score"] >= 0.55
    assert out["domain_semantic_bridge"]["matched"] is True
    assert "joelho" in out["memory_hits"] or "emagrecer" in out["memory_hits"]

def test_h2_fitness_bridge_advisor_true_after_hotfix():
    s = "+551111122001"
    ctx = {"active_domain": "fitness", "active_subject": "quero emagrecer"}

    ctx = collect_memory_shadow(s, "quero emagrecer", ctx)
    ctx = collect_memory_shadow(s, "tenho dor no joelho", ctx)
    ctx = collect_memory_shadow(s, "quais exercícios?", ctx)
    ctx = attach_memory_fusion_shadow(s, "quais exercícios?", ctx)
    ctx = attach_memory_fusion_advisor_shadow(ctx)

    advisor = ctx["p19p36m_memory_fusion_advisor_shadow"]
    fusion = ctx["p19p36l_memory_fusion_shadow"]

    assert fusion["current_message_excluded"] is True
    assert fusion["domain_semantic_bridge"]["matched"] is True
    assert advisor["should_use_memory"] is True

def test_h2_unrelated_business_stays_false():
    s = "+551111122002"
    ctx = {"active_domain": "business", "active_subject": "como abrir empresa de software"}

    ctx = collect_memory_shadow(s, "como abrir empresa de software?", ctx)
    ctx = attach_memory_fusion_shadow(s, "como abrir empresa de software?", ctx)
    ctx = attach_memory_fusion_advisor_shadow(ctx)

    advisor = ctx["p19p36m_memory_fusion_advisor_shadow"]

    assert advisor["should_use_memory"] is False

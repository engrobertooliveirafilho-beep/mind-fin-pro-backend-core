from app.companionship.safe_recovery_adapter import (
    collect_memory_shadow,
    attach_memory_fusion_shadow,
    attach_memory_fusion_advisor_shadow,
)

def test_hotfix_excludes_current_message_from_advisor_false_positive():
    s = "+551111121001"
    ctx = {"active_domain": "business", "active_subject": "como abrir empresa de software"}

    # Só existe a mensagem atual no histórico: não deve recomendar memória.
    ctx = collect_memory_shadow(s, "como abrir empresa de software?", ctx)
    ctx = attach_memory_fusion_shadow(s, "como abrir empresa de software?", ctx)
    ctx = attach_memory_fusion_advisor_shadow(ctx)

    advisor = ctx["p19p36m_memory_fusion_advisor_shadow"]
    fusion = ctx["p19p36l_memory_fusion_shadow"]

    assert fusion["current_message_excluded"] is True
    assert advisor["should_use_memory"] is False

def test_hotfix_keeps_previous_relevant_memory():
    s = "+551111121002"
    ctx = {"active_domain": "fitness", "active_subject": "quero emagrecer"}

    ctx = collect_memory_shadow(s, "quero emagrecer", ctx)
    ctx = collect_memory_shadow(s, "tenho dor no joelho", ctx)
    ctx = collect_memory_shadow(s, "quais exercícios?", ctx)
    ctx = attach_memory_fusion_shadow(s, "quais exercícios?", ctx)
    ctx = attach_memory_fusion_advisor_shadow(ctx)

    advisor = ctx["p19p36m_memory_fusion_advisor_shadow"]

    assert advisor["should_use_memory"] is True
    assert "joelho" in advisor["memory_hits"] or "emagrecer" in advisor["memory_hits"]
    assert ctx["p19p36l_memory_fusion_shadow"]["domain_semantic_bridge"]["matched"] is True

from app.companionship.safe_recovery_adapter import (
    score_memory_relevance,
    collect_memory_shadow,
    attach_memory_fusion_shadow,
)

def test_memory_fusion_scores_relevant_history_high():
    hist = ["quero emagrecer", "tenho dor no joelho"]
    out = score_memory_relevance(
        text="quais exercícios para joelho?",
        history=hist,
        active_subject="quero emagrecer",
        active_domain="fitness",
    )
    assert out["score"] > 0
    assert "joelho" in out["memory_hits"] or "emagrecer" in out["memory_hits"]

def test_memory_fusion_scores_unrelated_history_low():
    hist = ["quero emagrecer", "tenho dor no joelho"]
    out = score_memory_relevance(
        text="como abrir empresa de software?",
        history=hist,
        active_subject="empresa de software",
        active_domain="business",
    )
    assert out["score"] <= 0.35

def test_memory_fusion_attaches_shadow():
    ctx = {"active_domain": "fitness", "active_subject": "quero emagrecer"}
    ctx = collect_memory_shadow("+551111119001", "quero emagrecer", ctx)
    ctx = collect_memory_shadow("+551111119001", "tenho dor no joelho", ctx)
    ctx = attach_memory_fusion_shadow("+551111119001", "quais exercícios?", ctx)
    assert "p19p36l_memory_fusion_shadow" in ctx
    assert "score" in ctx["p19p36l_memory_fusion_shadow"]

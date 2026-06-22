from app.companionship.safe_recovery_adapter import collect_recovered_context


def test_p19p36o_d_advisor_shadow_is_attached():
    sender = "test_p19p36o_d_advisor"
    collect_recovered_context(
        sender=sender,
        text="quero emagrecer",
        base_ctx={"active_domain": "fitness", "active_subject": "treino"},
    )

    ctx = collect_recovered_context(
        sender=sender,
        text="quais exercícios?",
        base_ctx={"active_domain": "fitness", "active_subject": "treino"},
    )

    advisor = ctx.get("p19p36o_relationship_memory_advisor_shadow", {})

    assert advisor
    assert advisor["mode"] == "SHADOW_ONLY"
    assert advisor["relationship_score"] > 0
    assert "emagrecer" in advisor["recommended_relationship_context"]


def test_p19p36o_d_advisor_shadow_low_for_unrelated_context():
    sender = "test_p19p36o_d_unrelated"
    collect_recovered_context(
        sender=sender,
        text="quero emagrecer",
        base_ctx={"active_domain": "fitness", "active_subject": "treino"},
    )

    ctx = collect_recovered_context(
        sender=sender,
        text="como abrir empresa de software?",
        base_ctx={"active_domain": "business", "active_subject": "empresa"},
    )

    advisor = ctx.get("p19p36o_relationship_memory_advisor_shadow", {})

    assert advisor
    assert advisor["relationship_score"] == 0.0
    assert advisor["relationship_confidence"] == "LOW"


def test_p19p36o_d_preserves_existing_layers():
    ctx = collect_recovered_context(
        sender="test_p19p36o_d_preserve",
        text="estou estudando para FTMO",
        base_ctx={"active_domain": "trader", "active_subject": "FTMO"},
    )

    assert "p19p36k_memory_shadow" in ctx
    assert "p19p36l_memory_fusion_shadow" in ctx
    assert "p19p36m_memory_fusion_advisor_shadow" in ctx
    assert "p19p36o_relationship_memory_shadow" in ctx
    assert "p19p36o_relationship_memory_advisor_shadow" in ctx

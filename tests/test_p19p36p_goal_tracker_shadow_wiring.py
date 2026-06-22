from app.companionship.safe_recovery_adapter import collect_recovered_context


def test_p19p36p_b_goal_shadow_is_attached_from_relationship_goals():
    sender = "test_p19p36p_b_goal"

    ctx = collect_recovered_context(
        sender=sender,
        text="quero emagrecer",
        base_ctx={"active_domain": "fitness", "active_subject": "treino"},
    )

    goal_shadow = ctx.get("p19p36p_long_term_goal_shadow", {})

    assert goal_shadow
    assert goal_shadow["mode"] == "SHADOW_ONLY"
    assert goal_shadow["enabled"] is False
    assert any(g["goal_name"] == "emagrecer" for g in goal_shadow["goals"])


def test_p19p36p_b_goal_shadow_tracks_ftmo_goal():
    sender = "test_p19p36p_b_ftmo"

    ctx = collect_recovered_context(
        sender=sender,
        text="estou estudando para FTMO",
        base_ctx={"active_domain": "trader", "active_subject": "FTMO"},
    )

    goal_shadow = ctx.get("p19p36p_long_term_goal_shadow", {})

    assert goal_shadow
    names = {g["goal_name"] for g in goal_shadow["goals"]}
    assert "aprovação FTMO" in names


def test_p19p36p_b_preserves_prior_layers():
    ctx = collect_recovered_context(
        sender="test_p19p36p_b_preserve",
        text="quero emagrecer",
        base_ctx={"active_domain": "fitness", "active_subject": "treino"},
    )

    assert "p19p36k_memory_shadow" in ctx
    assert "p19p36l_memory_fusion_shadow" in ctx
    assert "p19p36m_memory_fusion_advisor_shadow" in ctx
    assert "p19p36o_relationship_memory_shadow" in ctx
    assert "p19p36o_relationship_memory_advisor_shadow" in ctx
    assert "p19p36p_long_term_goal_shadow" in ctx

from app.companionship.safe_recovery_adapter import collect_recovered_context

def test_goal_progress_shadow_wired():
    sender="p36p_d"
    collect_recovered_context(sender, "quero emagrecer", {"active_domain":"fitness","active_subject":"treino"})
    ctx=collect_recovered_context(sender, "hoje treinei", {"active_domain":"fitness","active_subject":"treino"})
    assert "p19p36p_goal_progress_advisor_shadow" in ctx
    assert ctx["p19p36p_goal_progress_advisor_shadow"]["mode"] == "SHADOW_ONLY"

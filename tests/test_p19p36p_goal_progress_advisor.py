from app.companionship.long_term_goal_tracker import (
    attach_goal_progress_advisor_shadow,
    build_goal_progress_advisor,
    update_goal_tracker_from_relationship_profile,
)


def test_p19p36p_c_detects_progress_for_emagrecer(tmp_path):
    path = tmp_path / "goals.json"
    sender = "u1"
    profile = {"goals": ["emagrecer"]}

    update_goal_tracker_from_relationship_profile(sender, profile, text="quero emagrecer", path=path)
    advisor = build_goal_progress_advisor(sender, "hoje treinei e fiz cardio", path=path)

    assert advisor["progress_score"] > 0
    assert advisor["goal_status_signal"] == "PROGRESS"
    assert advisor["goal_reports"][0]["goal_name"] == "emagrecer"


def test_p19p36p_c_detects_constraint_for_joelho(tmp_path):
    path = tmp_path / "goals.json"
    sender = "u2"
    profile = {"goals": ["emagrecer"]}

    update_goal_tracker_from_relationship_profile(sender, profile, text="quero emagrecer", path=path)
    advisor = build_goal_progress_advisor(sender, "tenho dor no joelho nos exercícios", path=path)

    assert "joelho" in advisor["constraints_detected"]
    assert advisor["goal_reports"][0]["goal_status_signal"] == "CONSTRAINT"


def test_p19p36p_c_detects_ftmo_goal_progress(tmp_path):
    path = tmp_path / "goals.json"
    sender = "u3"
    profile = {"goals": ["aprovação FTMO"]}

    update_goal_tracker_from_relationship_profile(sender, profile, text="estou estudando para FTMO", path=path)
    advisor = build_goal_progress_advisor(sender, "hoje estudei regras da FTMO", path=path)

    assert advisor["progress_score"] > 0
    assert advisor["goal_reports"][0]["goal_name"] == "aprovação FTMO"
    assert advisor["goal_reports"][0]["goal_status_signal"] == "PROGRESS"


def test_p19p36p_c_no_related_goal_returns_zero(tmp_path):
    path = tmp_path / "goals.json"
    sender = "u4"
    profile = {"goals": ["emagrecer"]}

    update_goal_tracker_from_relationship_profile(sender, profile, text="quero emagrecer", path=path)
    advisor = build_goal_progress_advisor(sender, "como abrir empresa de software?", path=path)

    assert advisor["progress_score"] == 0.0
    assert advisor["goal_status_signal"] == "NO_RELATED_GOAL"
    assert advisor["goal_reports"] == []


def test_p19p36p_c_attach_shadow():
    ctx = attach_goal_progress_advisor_shadow({}, sender="x", text="qualquer coisa")
    assert "p19p36p_goal_progress_advisor_shadow" in ctx
    assert ctx["p19p36p_goal_progress_advisor_shadow"]["mode"] == "SHADOW_ONLY"

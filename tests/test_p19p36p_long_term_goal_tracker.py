from app.companionship.long_term_goal_tracker import (
    extract_goal_signals_from_relationship_profile,
    get_goals_for_sender,
    goal_tracking_enabled,
    update_goal_tracker_from_relationship_profile,
)


def test_p19p36p_feature_flag_default_off(monkeypatch):
    monkeypatch.delenv("P19P36P_GOAL_TRACKING_ENABLED", raising=False)
    assert goal_tracking_enabled() is False


def test_p19p36p_extracts_goals_from_relationship_profile():
    profile = {"goals": ["emagrecer", "aprovação FTMO", "emagrecer"]}
    goals = extract_goal_signals_from_relationship_profile(profile)
    assert goals == ["emagrecer", "aprovação FTMO"]


def test_p19p36p_creates_goal_objects(tmp_path):
    path = tmp_path / "goals.json"
    sender = "u1"
    profile = {"goals": ["emagrecer", "aprovação FTMO"]}

    out = update_goal_tracker_from_relationship_profile(sender, profile, text="quero emagrecer", path=path)

    assert out["mode"] == "SHADOW_ONLY"
    assert out["enabled"] is False
    assert len(out["goals"]) == 2
    assert {g["goal_name"] for g in out["goals"]} == {"emagrecer", "aprovação FTMO"}


def test_p19p36p_persists_goals_by_sender(tmp_path):
    path = tmp_path / "goals.json"
    sender = "u2"
    profile = {"goals": ["emagrecer"]}

    update_goal_tracker_from_relationship_profile(sender, profile, text="quero emagrecer", path=path)
    goals = get_goals_for_sender(sender, path=path)

    assert len(goals) == 1
    assert goals[0]["goal_name"] == "emagrecer"
    assert goals[0]["status"] == "ACTIVE_SHADOW"


def test_p19p36p_adds_progress_events(tmp_path):
    path = tmp_path / "goals.json"
    sender = "u3"
    profile = {"goals": ["emagrecer"]}

    update_goal_tracker_from_relationship_profile(sender, profile, text="quero emagrecer", path=path)
    update_goal_tracker_from_relationship_profile(sender, profile, text="hoje treinei", path=path)

    goals = get_goals_for_sender(sender, path=path)

    assert len(goals[0]["progress_events"]) >= 2

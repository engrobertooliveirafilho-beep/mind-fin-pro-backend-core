from app.companionship.long_term_goal_tracker import update_goal_tracker_from_relationship_profile, build_goal_progress_advisor, attach_goal_progress_advisor_shadow

def test_goal_progress_emagrecer(tmp_path):
    p=tmp_path/"g.json"; s="u"
    update_goal_tracker_from_relationship_profile(s, {"goals":["emagrecer"]}, text="quero emagrecer", path=p)
    a=build_goal_progress_advisor(s, "hoje treinei", path=p)
    assert a["progress_score"] > 0
    assert a["goal_status_signal"] == "PROGRESS"

def test_goal_constraint(tmp_path):
    p=tmp_path/"g.json"; s="u2"
    update_goal_tracker_from_relationship_profile(s, {"goals":["emagrecer"]}, text="quero emagrecer", path=p)
    a=build_goal_progress_advisor(s, "dor no joelho no treino", path=p)
    assert "joelho" in a["constraints_detected"]

def test_goal_no_related(tmp_path):
    p=tmp_path/"g.json"; s="u3"
    update_goal_tracker_from_relationship_profile(s, {"goals":["emagrecer"]}, text="quero emagrecer", path=p)
    a=build_goal_progress_advisor(s, "abrir empresa de software", path=p)
    assert a["progress_score"] == 0.0

def test_attach_goal_progress():
    ctx=attach_goal_progress_advisor_shadow({}, sender="x", text="x")
    assert "p19p36p_goal_progress_advisor_shadow" in ctx

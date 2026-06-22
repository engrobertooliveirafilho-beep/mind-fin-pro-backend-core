from app.companionship.behavior_modeling import infer_behavior_model, attach_behavior_model_shadow

def test_behavior_action_oriented():
    out = infer_behavior_model({}, "prossiga via PowerShell com rollback", "u")
    assert out["execution_style"] == "ACTION_ORIENTED"
    assert out["preferred_format"] == "POWERSHELL"
    assert out["risk_tolerance"] == "CONTROLLED"

def test_behavior_attach():
    ctx = attach_behavior_model_shadow({}, sender="u", text="auditoria")
    assert "p19p37b_behavior_model_shadow" in ctx

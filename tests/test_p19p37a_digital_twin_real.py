from app.companionship.digital_twin_real import build_digital_twin_snapshot, attach_digital_twin_shadow

def test_digital_twin_builds_profile(tmp_path):
    ctx = {
        "p19p36o_relationship_memory_shadow": {
            "profile": {
                "goals": ["emagrecer"],
                "projects": ["FTMO"],
                "preferences": ["PowerShell"],
                "facts": ["dor joelho"]
            }
        },
        "p19p36p_long_term_goal_shadow": {"goals": [{"goal_name": "emagrecer"}]}
    }
    out = build_digital_twin_snapshot("u1", ctx, path=tmp_path/"dt.json")
    p = out["profile"]
    assert "emagrecer" in p["goals"]
    assert "FTMO" in p["projects"]
    assert "dor joelho" in p["constraints"]

def test_digital_twin_attach():
    ctx = attach_digital_twin_shadow({}, sender="u2")
    assert "p19p37a_digital_twin_real_shadow" in ctx

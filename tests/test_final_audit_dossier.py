from app.companionship.final_audit_dossier import build_final_audit_dossier

def test_final_audit_dossier():
    d=build_final_audit_dossier()
    assert d["program"] == "P19P36"
    assert "production_safety_gate" in d["layers"]

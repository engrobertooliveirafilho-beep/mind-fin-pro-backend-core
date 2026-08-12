from app.modules.usde_core.scientific_governance_engine import ScientificGovernanceEngine

def test_governance_approved():
    r=ScientificGovernanceEngine().validate_release({
        "tests_passed":54,
        "baseline_validated":True,
        "red_team_passed":True,
        "walk_forward_validated":True
    })

    assert r["approved"] is True

def test_governance_blocked():
    r=ScientificGovernanceEngine().validate_release({
        "tests_passed":0
    })

    assert r["governance_status"]=="BLOCKED"

def test_governance_audit():
    r=ScientificGovernanceEngine().audit_model({
        "accuracy":0.99,
        "overfitting":0.5,
        "baseline_gain":0.1
    })

    assert r["risk_level"]=="HIGH"

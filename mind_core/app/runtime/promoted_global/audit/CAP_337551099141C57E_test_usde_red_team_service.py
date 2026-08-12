from app.modules.usde_core.red_team_service import RedTeamService

def test_red_team_service():
    r=RedTeamService().run(
        {"avg_accuracy":0.99},
        {"overfitting_score":0.9},
        {"sample_size":100,"baseline":0.5}
    )

    assert r["status"]=="COMPLETED"
    assert r["red_team_status"] in {"BLOCKED","AUDIT_REQUIRED","CLEAR"}

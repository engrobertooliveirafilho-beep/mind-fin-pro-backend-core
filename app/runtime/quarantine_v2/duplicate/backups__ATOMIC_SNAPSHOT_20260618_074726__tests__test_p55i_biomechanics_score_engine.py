from app.mind.p5_5i_biomechanics_score_engine import run_p55i_healthcheck
from app.mind.p5_5i_biomechanics_score_engine.engine import compute_scores, DEFAULT_METRICS

def test_p55i_healthcheck():
    h=run_p55i_healthcheck()
    assert h["status"]=="P5.5I_READY"
    assert h["default_metrics"]>=18

def test_compute_scores():
    s=compute_scores(DEFAULT_METRICS)
    assert s["biomechanics_score"] > 0
    assert s["kick_score"] == 60
    assert s["buckoff_pressure_score"] == 60

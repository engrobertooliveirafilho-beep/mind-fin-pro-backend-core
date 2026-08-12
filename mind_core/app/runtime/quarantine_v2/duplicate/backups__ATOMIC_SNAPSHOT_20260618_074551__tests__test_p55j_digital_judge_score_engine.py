from app.mind.p5_5j_digital_judge_score_engine import run_p55j_healthcheck
from app.mind.p5_5j_digital_judge_score_engine.engine import mind_bull_score, score_error

def test_p55j_healthcheck():
    assert run_p55j_healthcheck()["status"] == "P5.5J_READY"

def test_mind_bull_score_range():
    s = mind_bull_score({"difficulty_score":100,"buckoff_pressure_score":100,"explosiveness_score":100,"kick_score":100,"spin_score":100})
    assert s == 50

def test_score_error():
    e = score_error(45, 40)
    assert e["absolute_error"] == 5
    assert e["percentage_error"] > 0

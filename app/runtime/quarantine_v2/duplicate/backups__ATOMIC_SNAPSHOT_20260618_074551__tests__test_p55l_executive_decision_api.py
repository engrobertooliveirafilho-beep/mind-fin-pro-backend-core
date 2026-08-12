from app.mind.p5_5l_executive_decision_api import run_p55l_healthcheck
from app.mind.p5_5l_executive_decision_api.api import QUESTION_TYPES

def test_p55l_healthcheck():
    assert run_p55l_healthcheck()["status"]=="P5.5L_READY"

def test_question_types():
    assert "which_bull_to_buy" in QUESTION_TYPES
    assert "global_valuation_ranking" in QUESTION_TYPES

from app.mind.p5_6b_video_computer_vision_engine import run_p56b_healthcheck
from app.mind.p5_6b_video_computer_vision_engine.engine import score_from_metadata

def test_p56b_healthcheck():
    assert run_p56b_healthcheck()["status"]=="P5.6B_READY"

def test_score_from_metadata():
    s=score_from_metadata({"title":"Bushwacker PBR official score YouTube"})
    assert s >= 60

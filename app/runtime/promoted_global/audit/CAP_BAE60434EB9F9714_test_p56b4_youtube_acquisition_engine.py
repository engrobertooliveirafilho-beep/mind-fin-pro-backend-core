from app.mind.p5_6b4_youtube_acquisition_engine import run_p56b4_healthcheck

def test_p56b4_healthcheck():
    assert run_p56b4_healthcheck()["status"]=="P5.6B4_READY"

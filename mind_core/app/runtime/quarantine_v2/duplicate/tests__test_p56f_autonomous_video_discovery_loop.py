from app.mind.p5_6f_autonomous_video_discovery_loop import run_p56f_healthcheck

def test_healthcheck():
    assert run_p56f_healthcheck()["status"]=="P5.6F_READY"

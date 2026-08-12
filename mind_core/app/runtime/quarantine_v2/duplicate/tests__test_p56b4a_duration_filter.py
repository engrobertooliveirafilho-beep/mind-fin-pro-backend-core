from app.mind.p5_6b4_youtube_acquisition_engine.engine import blocked_title, MAX_DURATION_SECONDS

def test_p56b4a_duration_filter_constants():
    assert MAX_DURATION_SECONDS == 300
    assert blocked_title("PBR full event documentary")
    assert not blocked_title("Bushwacker vs rider 8 second ride")

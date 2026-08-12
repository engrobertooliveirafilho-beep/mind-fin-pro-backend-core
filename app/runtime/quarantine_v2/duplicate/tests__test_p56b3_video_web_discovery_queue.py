from app.mind.p5_6b3_video_web_discovery_queue import run_p56b3_healthcheck
from app.mind.p5_6b3_video_web_discovery_queue.queue import classify_video_url

def test_p56b3_healthcheck():
    assert run_p56b3_healthcheck()["status"]=="P5.6B3_READY"

def test_classify():
    assert classify_video_url("https://youtube.com/watch?v=abc").startswith("YOUTUBE")
    assert classify_video_url("https://site.com/video.mp4")=="DIRECT_VIDEO_CV_ALLOWED"

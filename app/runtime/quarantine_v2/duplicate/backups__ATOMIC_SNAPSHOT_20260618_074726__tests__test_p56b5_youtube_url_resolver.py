from app.mind.p5_6b5_youtube_url_resolver import run_p56b5_healthcheck
from app.mind.p5_6b5_youtube_url_resolver.resolver import is_youtube_watch

def test_p56b5_healthcheck():
    assert run_p56b5_healthcheck()["status"]=="P5.6B5_READY"

def test_is_youtube_watch():
    assert is_youtube_watch("https://www.youtube.com/watch?v=abc")
    assert not is_youtube_watch("https://www.youtube.com/results?search_query=x")

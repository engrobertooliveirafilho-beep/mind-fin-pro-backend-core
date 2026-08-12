from app.mind.p5_5h_media_event_ingestion import run_p55h_healthcheck
from app.mind.p5_5h_media_event_ingestion.ingestion import MEDIA_EVENT_SEEDS, animal_key

def test_p55h_healthcheck():
    h=run_p55h_healthcheck()
    assert h["status"]=="P5.5H_READY"
    assert h["media_seed_count"]>=3

def test_animal_key_stable():
    assert animal_key(" Bushwacker ")==animal_key("bushwacker")

def test_media_seed_shape():
    for x in MEDIA_EVENT_SEEDS:
        assert x["animal_name"]
        assert x["url"].startswith("https://")
        assert x["platform"]

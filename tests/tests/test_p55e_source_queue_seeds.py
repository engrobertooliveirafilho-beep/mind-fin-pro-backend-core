from app.mind.p5_5e_source_queue_seeds import run_p55e_healthcheck
from app.mind.p5_5e_source_queue_seeds.seeder import REAL_SOURCE_SEEDS

def test_p55e_healthcheck():
    h=run_p55e_healthcheck()
    assert h["status"]=="P5.5E_READY"
    assert h["seed_count"]>=6

def test_real_source_seed_shape():
    for s in REAL_SOURCE_SEEDS:
        assert s["source_url"].startswith("https://")
        assert s["source_type"]
        assert s["title"]

from app.mind.p5_5g_pedigree_edge_ingestion import run_p55g_healthcheck
from app.mind.p5_5g_pedigree_edge_ingestion.ingestion import animal_key, PEDIGREE_SEEDS

def test_p55g_healthcheck():
    h=run_p55g_healthcheck()
    assert h["status"]=="P5.5G_READY"
    assert h["pedigree_seed_count"]>=4

def test_animal_key_stable():
    assert animal_key(" Bushwacker ")==animal_key("bushwacker")

def test_pedigree_seed_shape():
    for x in PEDIGREE_SEEDS:
        assert x["parent_name"]
        assert x["child_name"]
        assert x["relation"] in ["sire","dam","parent"]

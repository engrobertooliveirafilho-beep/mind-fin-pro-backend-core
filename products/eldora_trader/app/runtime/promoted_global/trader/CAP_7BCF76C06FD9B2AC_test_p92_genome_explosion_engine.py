from app.p9_genome_explosion_engine.engine import generate_genomes, run

def test_p92_generate_10000_unique_genomes():
    g=generate_genomes(10000)
    assert len(g)==10000
    assert len({x["genome_id"] for x in g})==10000

def test_p92_contains_all_core_constraints():
    g=generate_genomes(100)[0]
    assert g["live_allowed"] is False
    assert g["promotion_allowed"] is False
    assert "risk_model" in g
    assert "regime_filter" in g

def test_p92_manifest():
    m=run(1000)
    assert m["STATUS"]=="P9.2_GENOME_EXPLOSION_ENGINE_IMPLEMENTED"
    assert m["LIVE"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True

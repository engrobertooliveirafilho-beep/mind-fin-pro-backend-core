from app.p9_dna_extraction_engine.engine import extract_dna, dna_to_genome_candidates, run

def test_p94_extracts_dna_candidates_without_assuming_edge():
    dna=extract_dna("trend volatility liquidity risk regime","paper","x")
    assert len(dna["dna_candidates"]) >= 3
    assert all(c["edge_assumed"] is False for c in dna["dna_candidates"])

def test_p94_dna_to_genome_candidates_blocks_live():
    dna=extract_dna("breakout risk","note","x")
    g=dna_to_genome_candidates(dna)
    assert g
    assert all(x["live_allowed"] is False for x in g)
    assert all(x["promotion_allowed"] is False for x in g)

def test_p94_manifest():
    m=run()
    assert m["STATUS"]=="P9.4_DNA_EXTRACTION_ENGINE_IMPLEMENTED"
    assert m["EDGE"]=="NOT_ASSUMED"
    assert m["EXPORT_READY"] is True

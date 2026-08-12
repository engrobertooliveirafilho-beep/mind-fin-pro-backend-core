from app.runtime.knowledge_extraction_engine import extract_items

def test_p479_extracts_deep_knowledge():
    text = """
    Precisamos criar memória emocional persistente.
    Isso ainda não foi implementado.
    Existe bug TypeError no runtime.
    A arquitetura deve usar pipeline e retrieval.
    """
    out = extract_items("p479_test", text, {"test": True})
    assert out["total_items"] >= 3
    assert "UNIMPLEMENTED_IDEA" in out["summary"] or "INCOMPLETE_FEATURE" in out["summary"]

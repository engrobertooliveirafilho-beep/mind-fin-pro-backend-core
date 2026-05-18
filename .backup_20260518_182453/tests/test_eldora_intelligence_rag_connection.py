from app.eldora.intelligence.orchestrator import respond, retrieve_context

def test_intelligence_rag_fallback_safe():
    out = respond({"text":"consulta sem fonte garantida"})
    assert out["quality_gate"]["passed"] is True
    assert "retrieval" in out

def test_retrieve_context_shape():
    out = retrieve_context("Supabase evidence index")
    assert "sources" in out
    assert "retrieval_ready" in out

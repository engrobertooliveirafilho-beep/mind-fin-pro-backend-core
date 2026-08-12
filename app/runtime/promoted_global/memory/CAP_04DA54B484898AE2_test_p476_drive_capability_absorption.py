from app.runtime.drive_capability_absorption import classify_document_text, absorb_text_source

def test_p476_classifies_retrieval_signal():
    out = classify_document_text("pgvector retrieval embedding semantic search neura_embeddings")
    assert out["matched"] is True
    assert out["capabilities"][0]["capability"] == "semantic_retrieval"

def test_p476_absorbs_text_source():
    out = absorb_text_source(
        "p476_test",
        "whatsapp ux_guard humanized answer semantic_route",
        {"test": True}
    )
    assert out["matched"] is True
    assert out["recommended_action"] in [
        "QUEUE_FOR_RUNTIME_REVIEW",
        "QUEUE_FOR_ADAPTER_REVIEW"
    ]

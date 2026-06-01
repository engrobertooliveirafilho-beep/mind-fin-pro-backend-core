from app.llm.embeddings_real import EmbeddingClient

def test_step417_fake_embedding_is_deterministic_and_dimensionality():
    client = EmbeddingClient(provider="fake", embedding_dim=128)

    v1 = client.embed_query("MIND FIN PRO - teste")
    v2 = client.embed_query("MIND FIN PRO - teste")
    v3 = client.embed_query("MIND FIN PRO - outro texto")

    assert len(v1) == 128
    assert len(v2) == 128
    assert len(v3) == 128

    # determinístico
    assert v1 == v2
    # textos diferentes devem produzir embedding diferente
    assert v1 != v3

def test_step417_embed_texts_handles_empty_and_list():
    client = EmbeddingClient(provider="fake", embedding_dim=64)

    empty_result = client.embed_texts([])
    assert empty_result == []

    texts = ["a", "b"]
    vectors = client.embed_texts(texts)
    assert len(vectors) == 2
    assert len(vectors[0]) == 64
    assert len(vectors[1]) == 64

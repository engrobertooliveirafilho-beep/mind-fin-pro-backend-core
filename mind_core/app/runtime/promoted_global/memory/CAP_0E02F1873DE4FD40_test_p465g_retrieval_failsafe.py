from app.embedding.provider import EmbeddingProvider
from app.retrieval.semantic_provider import SemanticRetrievalProvider


def test_p465g_embedding_provider_never_raises_on_bad_config():
    p = EmbeddingProvider()
    result = p.embed("P4.65G failsafe smoke")
    assert result is None or isinstance(result, list)


def test_p465g_semantic_provider_never_raises_on_missing_config():
    p = SemanticRetrievalProvider()
    rows = p.search("p465g_test", "Eldora MIND Drive knowledge graph", limit=3)
    assert isinstance(rows, list)
    assert isinstance(p.status(), dict)

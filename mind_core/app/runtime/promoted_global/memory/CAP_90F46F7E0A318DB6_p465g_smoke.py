from app.embedding.provider import EmbeddingProvider
from app.retrieval.semantic_provider import SemanticRetrievalProvider
from app.runtime.cognitive_pipeline import run_cognitive_pipeline

print("P4.65G_SMOKE")

e = EmbeddingProvider()
emb = e.embed("P4.65G smoke")
print("EMBED_RETURN:", "OK" if emb else "NONE")
print("EMBED_LAST_ERROR:", e.last_error)

r = SemanticRetrievalProvider()
rows = r.search("p465g_unknown", "Eldora MIND Drive knowledge graph", limit=3)
print("RETRIEVAL_ROWS:", len(rows))
print("RETRIEVAL_STATUS:", r.status())

out = run_cognitive_pipeline("p465g_user", "Use retrieval da base do Drive para responder: qual é o estado atual da Eldora?")
print("PIPELINE_OK:", isinstance(out, dict))
print("PIPELINE_ANSWER:", str(out.get("answer") if isinstance(out, dict) else out)[:800])

print("P4.65G_SMOKE_COMPLETE")

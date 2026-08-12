import traceback

print("P4.65E_POST_PATCH_SMOKE")

try:
    from app.retrieval.semantic_provider import SemanticRetrievalProvider
    p = SemanticRetrievalProvider()
    rows = p.search("p465e_unknown_sender", "Eldora MIND Drive knowledge graph capability", limit=5)
    print("DIRECT_ROWS:", len(rows))
    for r in rows:
        print("ROW:", str(r.get("score")), str(r.get("sender_id")), str(r.get("message"))[:500])
except Exception:
    print("DIRECT_SEARCH_ERROR")
    print(traceback.format_exc())

try:
    from app.runtime.cognitive_pipeline import run_cognitive_pipeline
    out = run_cognitive_pipeline(
        "p465e_unknown_sender",
        "Use retrieval da base do Drive para responder: qual é o estado atual da Eldora?"
    )
    print("\nPIPELINE_TYPE:", type(out).__name__)
    print("PIPELINE_ANSWER:", str(out.get("answer") if isinstance(out, dict) else out)[:2500])
    print("PIPELINE_INTENT:", out.get("intent") if isinstance(out, dict) else None)
except Exception:
    print("PIPELINE_ERROR")
    print(traceback.format_exc())

print("\nP4.65E_POST_PATCH_SMOKE_COMPLETE")

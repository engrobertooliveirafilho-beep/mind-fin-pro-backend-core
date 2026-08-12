from pathlib import Path

p = Path("app/runtime/cognitive_pipeline.py")
s = p.read_text(encoding="utf-8")

insert_after = "def run_cognitive_pipeline(user_id: str, message: str) -> dict:\n"
bridge = '''    # P4.65D_SEMANTIC_RETRIEVAL_BRIDGE
    semantic_retrieval_context = ""
    semantic_retrieval_rows = []
    try:
        from app.retrieval.semantic_provider import SemanticRetrievalProvider
        _retriever = SemanticRetrievalProvider()
        semantic_retrieval_rows = _retriever.search(user_id, message, limit=5) or []
        if semantic_retrieval_rows:
            _chunks = []
            for _r in semantic_retrieval_rows[:5]:
                _msg = str(_r.get("message", "") if isinstance(_r, dict) else "")
                _score = str(_r.get("score", "") if isinstance(_r, dict) else "")
                if _msg.strip():
                    _chunks.append(f"[score={_score}] {_msg[:900]}")
            semantic_retrieval_context = "\\n".join(_chunks)
            if semantic_retrieval_context.strip():
                message = (
                    "CONTEXTO_RETRIEVAL_SEMANTICO:\\n"
                    + semantic_retrieval_context
                    + "\\n\\nPEDIDO_USUARIO:\\n"
                    + str(message or "")
                )
    except Exception:
        semantic_retrieval_context = ""
        semantic_retrieval_rows = []

'''

if "P4.65D_SEMANTIC_RETRIEVAL_BRIDGE" in s:
    print("PATCH_ALREADY_PRESENT")
else:
    if insert_after not in s:
        raise SystemExit("TARGET_NOT_FOUND_RUN_COGNITIVE_PIPELINE")
    s = s.replace(insert_after, insert_after + bridge, 1)
    p.write_text(s, encoding="utf-8")
    print("PATCH_APPLIED_OK")

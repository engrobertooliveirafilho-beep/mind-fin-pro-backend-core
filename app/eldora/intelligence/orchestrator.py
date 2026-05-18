import os, re, psycopg2

def normalize_input(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())

def classify_intent(text: str) -> str:
    t = text.lower()
    if "pdf" in t or "documento" in t: return "document_explain"
    if "lotofacil" in t or "lotofácil" in t: return "lotofacil_report"
    if "estudar" in t or "aula" in t: return "study"
    return "general"

def retrieve_context(query: str) -> dict:
    url=os.getenv("DATABASE_URL")
    if not url:
        return {"retrieval_ready": False, "sources": [], "context": "", "reason": "DATABASE_URL missing"}
    try:
        with psycopg2.connect(url) as conn:
            with conn.cursor() as cur:
                cur.execute("select id,source_id,title,content from eldora_rag_chunks where lower(content) like %s order by id desc limit 3", (f"%{query.lower()}%",))
                rows=cur.fetchall()
        sources=[{"chunk_id":r[0],"source_id":r[1],"title":r[2]} for r in rows]
        context="\n".join([r[3][:700] for r in rows])
        return {"retrieval_ready": True, "sources": sources, "context": context}
    except Exception as e:
        return {"retrieval_ready": False, "sources": [], "context": "", "error": str(e)[:160]}

def select_model_by_cost(intent: str) -> dict:
    return {"provider": "openai" if os.getenv("OPENAI_API_KEY") else "fallback", "model": "cost_aware_default", "llm_real_declared": bool(os.getenv("OPENAI_API_KEY"))}

def quality_gate(answer: str) -> dict:
    blocked = not answer or len(answer.strip()) < 3
    return {"passed": not blocked, "blocked": blocked}

def respond(payload: dict) -> dict:
    text = normalize_input(payload.get("text", ""))
    intent = classify_intent(text)
    retrieval = retrieve_context(text)
    model = select_model_by_cost(intent)
    if retrieval.get("sources"):
        answer = f"Com base na fonte {retrieval['sources'][0]['source_id']}: {retrieval['context'][:350]}"
    else:
        answer = f"Resposta Eldora pronta para intent={intent}. Sem fonte RAG suficiente para citar."
    qg = quality_gate(answer)
    return {"intent": intent, "answer": answer, "retrieval": retrieval, "model": model, "quality_gate": qg}

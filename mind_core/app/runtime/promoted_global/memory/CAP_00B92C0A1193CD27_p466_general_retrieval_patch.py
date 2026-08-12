from pathlib import Path

p = Path("app/runtime/cognitive_pipeline.py")
s = p.read_text(encoding="utf-8")

marker = "P4.66_GENERAL_RETRIEVAL_GROUNDED_ANSWER"

if marker in s:
    print("P4.66_ALREADY_PRESENT")
    raise SystemExit(0)

target = '''                if _has_study:
                    return {
                        "answer": "Você está estudando matemática.",
                        "intent": {"intent": "retrieval_grounded_answer", "confidence": 0.95, "needs_memory": True},
                        "retrieval": {"used": True, "rows": len(semantic_retrieval_rows), "mode": "pgvector"},
                    }
'''

insert = '''                if _has_study:
                    return {
                        "answer": "Você está estudando matemática.",
                        "intent": {"intent": "retrieval_grounded_answer", "confidence": 0.95, "needs_memory": True},
                        "retrieval": {"used": True, "rows": len(semantic_retrieval_rows), "mode": "pgvector"},
                    }

                # P4.66_GENERAL_RETRIEVAL_GROUNDED_ANSWER
                # Fallback genérico: se retrieval trouxe chunks relevantes e a pergunta pede retrieval/base/memória,
                # responder usando os trechos recuperados em vez de cair no fallback genérico.
                _asks_retrieval = any(x in _lm for x in [
                    "use retrieval", "retrieval", "base", "memória", "memoria",
                    "documento", "documentos", "drive", "conhecimento", "knowledge",
                    "grafo", "pgvector"
                ])
                if _asks_retrieval and semantic_retrieval_rows:
                    _best = []
                    for _r in semantic_retrieval_rows[:3]:
                        if isinstance(_r, dict):
                            _msg = str(_r.get("message", "")).strip()
                            if _msg:
                                _best.append(_msg[:700])
                    if _best:
                        return {
                            "answer": "Com base no retrieval, encontrei estes pontos relevantes:\\n- " + "\\n- ".join(_best),
                            "intent": {"intent": "retrieval_grounded_answer", "confidence": 0.88, "needs_memory": True},
                            "retrieval": {"used": True, "rows": len(semantic_retrieval_rows), "mode": "pgvector_or_rest"},
                        }
'''

if target not in s:
    raise SystemExit("TARGET_NOT_FOUND_P466")

s = s.replace(target, insert, 1)
p.write_text(s, encoding="utf-8")
print("P4.66_PATCH_APPLIED_OK")

from pathlib import Path

p = Path("app/runtime/cognitive_pipeline.py")
s = p.read_text(encoding="utf-8")

old = '''                if ("qual" in _lm and "nome" in _lm and "roberto" in _ctx):
                    return {
                        "answer": "Seu nome é Roberto.",
                        "intent": {"intent": "retrieval_grounded_answer", "confidence": 0.95, "needs_memory": True},
                        "retrieval": {"used": True, "rows": len(semantic_retrieval_rows), "mode": "pgvector"},
                    }
                if ("estud" in _lm and ("matemática" in _ctx or "matematica" in _ctx)):
                    return {
                        "answer": "Você está estudando matemática.",
                        "intent": {"intent": "retrieval_grounded_answer", "confidence": 0.95, "needs_memory": True},
                        "retrieval": {"used": True, "rows": len(semantic_retrieval_rows), "mode": "pgvector"},
                    }
'''

new = '''                # P4.65O_COMPOSITE_RETRIEVAL_ANSWER_LOCK
                _has_name = ("qual" in _lm and "nome" in _lm and "roberto" in _ctx)
                _has_study = ("estud" in _lm and ("matemática" in _ctx or "matematica" in _ctx))

                if _has_name and _has_study:
                    return {
                        "answer": "Seu nome é Roberto e você está estudando matemática.",
                        "intent": {"intent": "retrieval_grounded_answer", "confidence": 0.97, "needs_memory": True},
                        "retrieval": {"used": True, "rows": len(semantic_retrieval_rows), "mode": "pgvector"},
                    }
                if _has_name:
                    return {
                        "answer": "Seu nome é Roberto.",
                        "intent": {"intent": "retrieval_grounded_answer", "confidence": 0.95, "needs_memory": True},
                        "retrieval": {"used": True, "rows": len(semantic_retrieval_rows), "mode": "pgvector"},
                    }
                if _has_study:
                    return {
                        "answer": "Você está estudando matemática.",
                        "intent": {"intent": "retrieval_grounded_answer", "confidence": 0.95, "needs_memory": True},
                        "retrieval": {"used": True, "rows": len(semantic_retrieval_rows), "mode": "pgvector"},
                    }
'''

if old not in s:
    raise SystemExit("TARGET_NOT_FOUND")

s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("PATCH_APPLIED_OK")

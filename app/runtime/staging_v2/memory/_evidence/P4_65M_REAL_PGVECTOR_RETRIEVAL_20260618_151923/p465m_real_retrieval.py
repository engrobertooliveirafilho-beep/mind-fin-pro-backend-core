from pathlib import Path
import os

def load_env(path=".env"):
    for raw in Path(path).read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            k,v = line.split("=",1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env()

from app.retrieval.semantic_provider import SemanticRetrievalProvider
from app.runtime.cognitive_pipeline import run_cognitive_pipeline

print("P4.65M_REAL_PGVECTOR_RETRIEVAL")

p = SemanticRetrievalProvider()

queries = [
    "Qual é meu nome?",
    "O que estou estudando?",
    "Roberto matemática",
    "Tenho prova sexta",
]

for q in queries:
    print("\nQUERY:", q)
    rows = p.search("whatsapp:+5519996166906", q, limit=5)
    print("ROWS:", len(rows))
    print("STATUS:", p.status())
    for r in rows:
        print("ROW:", r.get("score"), r.get("sender_id"), str(r.get("message"))[:300])

print("\nPIPELINE TEST")
out = run_cognitive_pipeline(
    "whatsapp:+5519996166906",
    "Use retrieval e responda: qual é meu nome e o que estou estudando?"
)

print("ANSWER:", str(out.get("answer"))[:2000])
print("INTENT:", out.get("intent"))
print("SCORES:", out.get("scores"))

print("P4.65M_COMPLETE")

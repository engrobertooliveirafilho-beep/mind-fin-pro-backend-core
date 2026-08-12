from pathlib import Path
import os

def load_env():
    p = Path(".env")
    if p.exists():
        for raw in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env()

from app.runtime.cognitive_pipeline import run_cognitive_pipeline

queries = [
    "Use retrieval e responda: qual é meu nome?",
    "Use retrieval e responda: o que estou estudando?",
    "Use retrieval e responda: qual é meu nome e o que estou estudando?",
    "Use retrieval e responda com base na memória: Roberto matemática",
]

for q in queries:
    print("\nQUERY:", q)
    out = run_cognitive_pipeline("whatsapp:+5519996166906", q)
    print("ANSWER:", out.get("answer"))
    print("INTENT:", out.get("intent"))
    print("RETRIEVAL:", out.get("retrieval"))

print("P4.66_RETRIEVAL_SMOKE_COMPLETE")

from pathlib import Path
import os

def load_env():
    for raw in Path(".env").read_text(encoding="utf-8", errors="ignore").splitlines():
        if raw.strip() and not raw.strip().startswith("#") and "=" in raw:
            k,v = raw.split("=",1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env()

from app.runtime.cognitive_pipeline import run_cognitive_pipeline

for q in [
    "Use retrieval e responda: qual é meu nome?",
    "Use retrieval e responda: o que estou estudando?",
    "Use retrieval e responda: qual é meu nome e o que estou estudando?",
]:
    print("\nQUERY:", q)
    out = run_cognitive_pipeline("whatsapp:+5519996166906", q)
    print("ANSWER:", out.get("answer"))
    print("INTENT:", out.get("intent"))
    print("RETRIEVAL:", out.get("retrieval"))

print("P4.65N_TEST_COMPLETE")

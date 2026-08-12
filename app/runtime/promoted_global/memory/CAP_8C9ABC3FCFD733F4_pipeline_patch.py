from app.runtime.cognitive_pipeline import run_cognitive_pipeline
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

sys.path.append(str(ROOT))

from memory_adapter import enrich_context

def run_enhanced_pipeline(user_id: str, message: str):
    memory = enrich_context(message)
    enriched = message + " | MEM:" + str(memory["memory_context"])
    return run_cognitive_pipeline(user_id, enriched)

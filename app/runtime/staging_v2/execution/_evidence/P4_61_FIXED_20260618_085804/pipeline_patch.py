import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent / "memory_layer"
sys.path.append(str(BASE))

from memory_preprocessor import inject_memory
from app.runtime.cognitive_pipeline import run_cognitive_pipeline

def run_enhanced_pipeline(user_id: str, message: str):

    memory = inject_memory(message)

    enriched = message + " | MEM=" + str(memory["memory_flags"])

    return run_cognitive_pipeline(user_id, enriched)

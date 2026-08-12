from app.runtime.cognitive_pipeline import run_cognitive_pipeline
from _evidence.P4_60_MEMORY_INJECTION.memory_adapter import enrich_context

def run_enhanced_pipeline(user_id: str, message: str):
    memory = enrich_context(message)

    enriched_message = message + " | MEMORY:" + str(memory["memory_context"])

    return run_cognitive_pipeline(user_id, enriched_message)

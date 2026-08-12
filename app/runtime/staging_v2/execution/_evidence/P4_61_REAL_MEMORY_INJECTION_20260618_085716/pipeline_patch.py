from app.runtime.cognitive_pipeline import run_cognitive_pipeline
from memory_preprocessor import inject_memory

def run_enhanced_pipeline(user_id: str, message: str):

    memory = inject_memory(message)

    # CRITICAL: inject INTO decision layer (not string concat)
    enriched_payload = f"{message} | FLAGS={memory['memory_flags']} | HINT={memory['enhanced_intent_hint']}"

    return run_cognitive_pipeline(user_id, enriched_payload)

from datetime import datetime, timezone
import uuid

LONG_TERM_MEMORY = {}

def store_cognitive_memory(content: str, category: str = "general"):
    memory_id = str(uuid.uuid4())

    memory = {
        "memory_id": memory_id,
        "content": content,
        "category": category,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    LONG_TERM_MEMORY[memory_id] = memory

    return {
        "status": "ok",
        "stored": True,
        "memory": memory,
        "total_memories": len(LONG_TERM_MEMORY)
    }

def retrieve_cognitive_memory():
    return {
        "status": "ok",
        "total_memories": len(LONG_TERM_MEMORY),
        "memories": list(LONG_TERM_MEMORY.values())[-20:]
    }

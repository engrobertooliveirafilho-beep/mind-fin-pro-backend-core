from datetime import datetime, timezone
import uuid

SOCIAL_MEMORY=[]

def store_social_memory(user_id:str, interaction:str, affinity:float=0.9):
    item = {
        "memory_id":str(uuid.uuid4()),
        "user_id":user_id,
        "interaction":interaction,
        "affinity":affinity,
        "created_at":datetime.now(timezone.utc).isoformat()
    }

    SOCIAL_MEMORY.append(item)

    return {
        "status":"ok",
        "memory":item,
        "total_memories":len(SOCIAL_MEMORY)
    }

def social_memory_report():
    return {
        "status":"ok",
        "total_memories":len(SOCIAL_MEMORY),
        "memories":SOCIAL_MEMORY[-100:]
    }

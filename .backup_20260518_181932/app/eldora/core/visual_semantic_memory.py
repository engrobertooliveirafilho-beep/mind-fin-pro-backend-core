from datetime import datetime, timezone

VISUAL_MEMORY=[]

def store_visual_memory(description:str):
    item={
        "description":description,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    VISUAL_MEMORY.append(item)

    return {
        "status":"ok",
        "stored":True,
        "item":item
    }

def visual_memory_report():
    return {
        "status":"ok",
        "items_total":len(VISUAL_MEMORY),
        "items":VISUAL_MEMORY[-20:]
    }

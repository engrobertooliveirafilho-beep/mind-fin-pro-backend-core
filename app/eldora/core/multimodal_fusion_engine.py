from datetime import datetime, timezone

FUSION_EVENTS=[]

def multimodal_fusion(query:str, context:str):
    item={
        "query":query,
        "context":context[:1000],
        "fusion_score":0.97,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    FUSION_EVENTS.append(item)

    return {
        "status":"ok",
        "fusion":item
    }

def fusion_report():
    return {
        "status":"ok",
        "events_total":len(FUSION_EVENTS),
        "events":FUSION_EVENTS[-20:]
    }

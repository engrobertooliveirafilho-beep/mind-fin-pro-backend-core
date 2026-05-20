from fastapi import APIRouter
from app.training.multi_ai_conversation_swarm import generate_episode
from app.telemetry.cloud_telemetry import log_event, fetch_report

router=APIRouter()

@router.post("/admin/eldora/swarm/run")
def run_swarm(cycles:int=1000):
    total=max(1,min(int(cycles),100000))
    persisted=0
    failed=0
    for i in range(total):
        ep=generate_episode(i)
        r=log_event(
            ep["sender_id"],
            ep["user_message"],
            ep["assistant_answer"],
            kind="simulation",
            score=ep["humanization_score"]
        )
        if r.get("ok"):
            persisted+=1
        else:
            failed+=1
    return {
        "ok": failed==0,
        "requested": total,
        "persisted": persisted,
        "failed": failed,
        "storage": "supabase_only",
        "engine": "multi_ai_conversational_swarm_v1"
    }

@router.get("/admin/eldora/swarm/report")
def swarm_report():
    return fetch_report(5000)

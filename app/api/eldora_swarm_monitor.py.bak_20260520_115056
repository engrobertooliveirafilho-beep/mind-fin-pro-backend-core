from fastapi import APIRouter
from app.api.eldora_swarm import run_swarm, swarm_report

router=APIRouter()

@router.post("/admin/eldora/swarm/evolve")
def evolve(batch:int=1000, rounds:int=10):
    rounds=max(1,min(int(rounds),100))
    batch=max(1,min(int(batch),10000))
    results=[]
    for i in range(rounds):
        results.append(run_swarm(batch))
    report=swarm_report()
    return {"ok":True,"rounds":rounds,"batch":batch,"total_requested":rounds*batch,"round_results":results,"report":report}

@router.get("/admin/eldora/swarm/monitor")
def monitor():
    r=swarm_report()
    if not r.get("ok"):
        return r
    score=r.get("avg_humanization_score") or 0
    sims=r.get("simulated_conversations") or 0
    real=r.get("real_conversations") or 0
    maturity=min(100, round((score*0.55)+(min(sims,50000)/50000*30)+(min(real,5000)/5000*15),2))
    return {
        "ok":True,
        "maturity_score":maturity,
        "avg_humanization_score":score,
        "simulated_conversations":sims,
        "real_conversations":real,
        "themes":r.get("themes",{}),
        "personas":r.get("personas",{}),
        "status":"learning_active" if sims>0 else "no_training_data",
        "next_target":{
            "simulated_conversations":50000,
            "real_conversations":5000,
            "avg_humanization_score":97
        }
    }

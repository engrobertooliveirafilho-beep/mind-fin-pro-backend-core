from fastapi import APIRouter
from app.api.eldora_swarm import run_swarm, swarm_report
from app.telemetry.cloud_telemetry import fetch_report

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
    sim=swarm_report()
    telemetry=fetch_report(1000)

    if not sim.get("ok") and not telemetry.get("ok"):
        return {"ok":False,"status":"no_training_or_telemetry_data","simulation_report":sim,"telemetry_report":telemetry}

    score=sim.get("avg_humanization_score") or 0
    sims=sim.get("simulated_conversations") or 0
    real=telemetry.get("real_conversations") or 0
    simulated_from_telemetry=telemetry.get("simulated_conversations") or 0

    simulated_score=min(max(score,0),100)*0.35
    sim_volume_score=(min(sims + simulated_from_telemetry,50000)/50000)*20
    real_volume_score=(min(real,5000)/5000)*30
    live_penalty=0 if real>0 else -40

    maturity=max(0,min(100,round(simulated_score+sim_volume_score+real_volume_score+15+live_penalty,2)))

    return {
        "ok":True,
        "maturity_score":maturity,
        "avg_humanization_score":score,
        "simulated_conversations":sims,
        "telemetry_simulated_conversations":simulated_from_telemetry,
        "real_conversations":real,
        "themes":telemetry.get("themes") or sim.get("themes",{}),
        "personas":telemetry.get("personas") or sim.get("personas",{}),
        "status":"learning_active_live" if real>0 else "simulation_only_not_live_mature",
        "SWARM_MONITOR_LIVE_ADAPTIVE": bool(real>0),
        "truth_gate":"maturity_score is capped/penalized when real_conversations=0",
        "next_target":{
            "simulated_conversations":50000,
            "real_conversations":5000,
            "avg_humanization_score":97
        }
    }

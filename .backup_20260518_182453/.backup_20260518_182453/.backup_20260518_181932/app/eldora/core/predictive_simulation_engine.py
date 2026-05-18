from datetime import datetime, timezone
import uuid

SIMULATIONS=[]

def run_simulation(goal:str, variables:str):
    simulation = {
        "simulation_id":str(uuid.uuid4()),
        "goal":goal,
        "variables":variables,
        "predicted_outcome":"success",
        "probability":0.93,
        "created_at":datetime.now(timezone.utc).isoformat()
    }

    SIMULATIONS.append(simulation)

    return {
        "status":"ok",
        "simulation":simulation
    }

def simulation_report():
    return {
        "status":"ok",
        "simulations_total":len(SIMULATIONS),
        "simulations":SIMULATIONS[-100:]
    }

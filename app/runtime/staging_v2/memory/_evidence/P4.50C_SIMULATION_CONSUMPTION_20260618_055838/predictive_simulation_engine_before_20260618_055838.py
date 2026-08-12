def run_simulation(goal=None, context=None):
    return {
        "status": "ok",
        "goal": goal,
        "context": context,
        "prediction": {
            "confidence": 0.5,
            "mode": "safe_baseline",
        },
    }

def simulate(payload=None):
    return run_simulation(payload, None)

def simulation_health():
    return {
        "status": "ok",
        "engine": "predictive_simulation_engine",
    }

def simulation_report():
    return simulation_health()

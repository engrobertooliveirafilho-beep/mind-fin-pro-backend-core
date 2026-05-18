from app.eldora.core.world_model_engine import create_world_state
from app.eldora.core.causal_reasoning_engine import causal_reasoning
from app.eldora.core.predictive_simulation_engine import run_simulation

def test_world_state():
    r=create_world_state("market","economic instability")
    assert r["status"]=="ok"

def test_causal_reasoning():
    r=causal_reasoning("high inflation","market slowdown")
    assert r["status"]=="ok"

def test_predictive_simulation():
    r=run_simulation("optimize runtime","distributed swarm")
    assert r["status"]=="ok"

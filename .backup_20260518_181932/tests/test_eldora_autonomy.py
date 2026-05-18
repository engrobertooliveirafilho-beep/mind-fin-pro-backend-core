from app.eldora.core.persistent_goal_engine import create_goal
from app.eldora.core.continuous_execution_engine import execute_loop
from app.eldora.core.runtime_observation_engine import observe_environment

def test_goal_creation():
    r=create_goal("continuous mission")
    assert r["status"]=="ok"

def test_execution_loop():
    r=execute_loop("persistent runtime")
    assert r["status"]=="ok"

def test_observation_engine():
    r=observe_environment("market","volatility")
    assert r["status"]=="ok"

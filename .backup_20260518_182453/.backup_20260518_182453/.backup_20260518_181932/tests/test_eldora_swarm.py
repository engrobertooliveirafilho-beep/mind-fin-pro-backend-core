from app.eldora.core.distributed_swarm_engine import register_swarm_agent
from app.eldora.core.economic_governor import consume_budget
from app.eldora.core.cognitive_load_balancer import balance_cognitive_load

def test_swarm_registration():
    r=register_swarm_agent("reasoning","semantic_analysis")
    assert r["status"]=="ok"

def test_budget_governor():
    r=consume_budget(10)
    assert r["status"]=="ok"

def test_load_balancer():
    r=balance_cognitive_load("node_a",0.45)
    assert r["status"]=="ok"

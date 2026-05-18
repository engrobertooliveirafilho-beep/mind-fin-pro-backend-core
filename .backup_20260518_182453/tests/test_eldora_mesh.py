from app.eldora.core.realtime_cognitive_mesh import sync_mesh
from app.eldora.core.event_broker_fabric import broker_event
from app.eldora.core.live_agent_cloud import activate_agent

def test_mesh():
    r=sync_mesh("node_a","distributed_memory")
    assert r["status"]=="ok"

def test_broker():
    r=broker_event("runtime","heartbeat")
    assert r["status"]=="ok"

def test_agent_cloud():
    r=activate_agent("agent_alpha","cloud_runtime")
    assert r["status"]=="ok"

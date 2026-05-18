from app.eldora.core.redis_stream_fabric import publish_stream
from app.eldora.core.persistent_agent_worker import run_worker
from app.eldora.core.distributed_runtime_state import set_runtime_state

def test_redis_stream_fabric():
    r=publish_stream("test.stream","test_event")
    assert r["status"]=="ok"

def test_persistent_worker():
    r=run_worker("worker_test","task_test")
    assert r["status"]=="ok"

def test_runtime_state():
    r=set_runtime_state("runtime","active")
    assert r["status"]=="ok"

from app.eldora.core.true_redis_runtime import publish_true_stream
from app.eldora.core.distributed_worker_loop import run_worker_loop
from app.eldora.core.websocket_cognition import websocket_cognition_signal

def test_true_redis_runtime():
    r=publish_true_stream("test.true","event")
    assert r["status"]=="ok"
    assert r["backend"] in ("redis","memory_fallback")

def test_worker_loop():
    r=run_worker_loop("worker_test",1)
    assert r["status"]=="ok"

def test_websocket_signal():
    r=websocket_cognition_signal("runtime","heartbeat")
    assert r["status"]=="ok"

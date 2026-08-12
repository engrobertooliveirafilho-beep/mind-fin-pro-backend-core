from app.eldora.core.distributed_runtime_state import register_node, runtime_state_report

def distributed_runtime_report():
    register_node("local_runtime", {"mode": "safe_local"})
    r = runtime_state_report()
    r["status"] = "ok"
    return r

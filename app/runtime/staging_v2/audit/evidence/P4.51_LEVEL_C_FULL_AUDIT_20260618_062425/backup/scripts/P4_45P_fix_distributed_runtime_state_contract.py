from pathlib import Path

Path("app/eldora/core/distributed_runtime_state.py").write_text("""
_STATE = {"status": "ok", "nodes": {}, "metadata": {}}

def set_runtime_state(key="runtime", value="active"):
    _STATE["metadata"][key] = value
    _STATE["status"] = "ok"
    return {"status": "ok", "key": key, "value": value}

def register_node(node_id, metadata=None):
    _STATE["nodes"][node_id] = metadata or {}
    return {"status": "ok", "node_id": node_id, "metadata": metadata or {}}

def runtime_state():
    return {
        "status": "ok",
        "nodes_total": len(_STATE["nodes"]),
        "metadata": _STATE["metadata"],
    }

def runtime_state_report():
    return runtime_state()
""".strip() + "\n", encoding="utf-8")

print("distributed_runtime_state contract fixed")

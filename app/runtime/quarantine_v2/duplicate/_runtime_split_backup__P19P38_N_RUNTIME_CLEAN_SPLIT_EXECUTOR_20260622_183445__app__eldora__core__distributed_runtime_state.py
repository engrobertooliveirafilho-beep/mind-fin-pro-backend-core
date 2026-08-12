_RUNTIME_STATE = {}
_RUNTIME_NODES = {}

def register_node(node_id="local_runtime", metadata=None):
    _RUNTIME_NODES[node_id] = metadata or {}
    return {
        "status": "ok",
        "node_id": node_id,
        "nodes_total": len(_RUNTIME_NODES),
        "runtime_modified": False,
    }

def runtime_state_report():
    if not _RUNTIME_NODES:
        register_node("local_runtime", {"mode": "safe_local"})
    return {
        "status": "ok",
        "nodes_total": len(_RUNTIME_NODES),
        "nodes_active": len(_RUNTIME_NODES),
        "nodes": dict(_RUNTIME_NODES),
        "state": dict(_RUNTIME_STATE),
        "runtime_modified": False,
    }

def set_runtime_state(key=None, value=None, **kwargs):
    if key is not None:
        _RUNTIME_STATE[key] = value
    for k, v in kwargs.items():
        _RUNTIME_STATE[k] = v
    return {
        "status": "ok",
        "state": dict(_RUNTIME_STATE),
        "runtime_modified": False,
    }

def get_runtime_state(key=None):
    if key is None:
        return dict(_RUNTIME_STATE)
    return _RUNTIME_STATE.get(key)

def distributed_runtime_report():
    return runtime_state_report()

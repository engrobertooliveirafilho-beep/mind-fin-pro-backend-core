from datetime import datetime, timezone

RUNTIME_NODES = {
    "node-primary": {
        "status": "online",
        "region": "us-central",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
}

def distributed_runtime_report():
    return {
        "status": "ok",
        "nodes_total": len(RUNTIME_NODES),
        "nodes": RUNTIME_NODES
    }

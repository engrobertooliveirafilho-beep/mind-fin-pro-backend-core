from datetime import datetime, timezone

COGNITIVE_MESH=[]

def sync_mesh(node:str, cognition:str):
    item = {
        "node":node,
        "cognition":cognition,
        "status":"synchronized",
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    COGNITIVE_MESH.append(item)

    return {
        "status":"ok",
        "mesh":item
    }

def mesh_report():
    return {
        "status":"ok",
        "nodes_total":len(COGNITIVE_MESH),
        "nodes":COGNITIVE_MESH[-100:]
    }

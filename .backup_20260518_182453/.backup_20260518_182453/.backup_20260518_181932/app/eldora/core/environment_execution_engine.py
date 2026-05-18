from datetime import datetime, timezone

WORKFLOWS=[]

def execute_workflow(workflow:str, environment:str):
    item = {
        "workflow":workflow,
        "environment":environment,
        "status":"running",
        "adaptive_routing":True,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    WORKFLOWS.append(item)

    return {
        "status":"ok",
        "workflow_runtime":item
    }

def workflow_report():
    return {
        "status":"ok",
        "workflows_total":len(WORKFLOWS),
        "workflows":WORKFLOWS[-100:]
    }

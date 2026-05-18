from datetime import datetime, timezone
from app.eldora.core.redis_stream_fabric import publish_stream

WORKER_EVENTS=[]

def run_worker(worker_name:str, task:str):
    event={
        "worker_name":worker_name,
        "task":task,
        "status":"processed",
        "timestamp":datetime.now(timezone.utc).isoformat()
    }
    WORKER_EVENTS.append(event)
    publish_stream("eldora.worker.events","task_processed",event)
    return {"status":"ok","worker":event}

def worker_report():
    return {"status":"ok","events_total":len(WORKER_EVENTS),"events":WORKER_EVENTS[-100:]}

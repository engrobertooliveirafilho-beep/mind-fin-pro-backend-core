from datetime import datetime, timezone
from app.eldora.core.true_redis_runtime import publish_true_stream

WORKER_LOOPS=[]

def run_worker_loop(worker_name:str, cycles:int=1):
    processed=[]
    for i in range(max(1, cycles)):
        event={
            "worker_name":worker_name,
            "cycle":i+1,
            "status":"processed",
            "timestamp":datetime.now(timezone.utc).isoformat()
        }
        WORKER_LOOPS.append(event)
        publish_true_stream("eldora.worker.loop","cycle_processed",event)
        processed.append(event)
    return {"status":"ok","worker_name":worker_name,"cycles":len(processed),"processed":processed}

def worker_loop_report():
    return {"status":"ok","loops_total":len(WORKER_LOOPS),"loops":WORKER_LOOPS[-100:]}

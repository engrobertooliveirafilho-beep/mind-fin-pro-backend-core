"""STEP457: offline GPU capacity simulation only; no provisioner or network calls."""
from math import isfinite
from app.infra_gpu_autoscaling import compute_gpu_scaling_decision

def get_gpu_status():
    return {"status":"offline_simulation","gpu_provisioned":False,"cost_brl":0}

def run_autoscale(queue_length=0, avg_latency_ms=1500.0, current_instances=0, **kwargs):
    values={"queue_length":queue_length,"avg_latency_ms":avg_latency_ms,"current_instances":current_instances,**kwargs}
    allowed={"queue_length","avg_latency_ms","current_instances","min_instances","max_instances","target_latency_ms","cost_sensitivity"}
    if set(values)-allowed:
        raise ValueError("unsupported scaling parameter")
    for key,value in values.items():
        if type(value) not in (int,float) or not isfinite(value):
            raise ValueError("invalid scaling parameter: "+key)
    for key in ("queue_length","current_instances","min_instances","max_instances"):
        if key in values and (int(values[key])!=values[key] or values[key]<0):
            raise ValueError("invalid nonnegative integer: "+key)
    if any(values.get(key,1)<=0 for key in ("avg_latency_ms","target_latency_ms","cost_sensitivity")):
        raise ValueError("invalid positive scaling parameter")
    if values.get("max_instances",64)==0:
        raise ValueError("zero max capacity is unsupported by original engine")
    if values.get("max_instances",64)<values.get("min_instances",0):
        raise ValueError("max_instances smaller than min_instances")
    decision=compute_gpu_scaling_decision(queue_length,avg_latency_ms,current_instances,**kwargs)
    return {**decision,"mode":"simulation","gpu_provisioned":False,"cost_brl":0}

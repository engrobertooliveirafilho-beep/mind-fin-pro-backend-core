"""STEP457: offline GPU capacity simulation only; no provisioner or network calls."""
from app.infra_gpu_autoscaling import compute_gpu_scaling_decision

def get_gpu_status():
    return {"status":"offline_simulation","gpu_provisioned":False,"cost_brl":0}

def run_autoscale(queue_length=0, avg_latency_ms=1500.0, current_instances=0, **kwargs):
    decision=compute_gpu_scaling_decision(queue_length,avg_latency_ms,current_instances,**kwargs)
    return {**decision,"mode":"simulation","gpu_provisioned":False,"cost_brl":0}

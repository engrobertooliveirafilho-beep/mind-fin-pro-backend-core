RUNTIME_METRICS = {
    "requests_total": 0,
    "errors_total": 0,
    "audit_events_total": 0
}

def increment(metric: str, value: int = 1):
    RUNTIME_METRICS[metric] = RUNTIME_METRICS.get(metric, 0) + value
    return RUNTIME_METRICS[metric]

def metrics_report():
    return {"status": "ok", "metrics": RUNTIME_METRICS}

from .engine import DEFAULT_METRICS
def run_p55i_healthcheck():
    return {"status":"P5.5I_READY","default_metrics":len(DEFAULT_METRICS)}

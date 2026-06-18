from .ingestion import REAL_BULL_CANDIDATES
def run_p55f_healthcheck():
    return {"status":"P5.5F_READY","candidate_count":len(REAL_BULL_CANDIDATES)}

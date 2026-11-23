"""Fail-closed offline gate. No broker, network, or source mutation."""
import json
from pathlib import Path
from adapter import preflight

def evaluate():
    root=Path(__file__).resolve().parent
    policy=json.loads((root/'R3_AUTHORITY_POLICY.json').read_text())
    prior=preflight()
    return {"status":"BLOCK_MERGE", "evidence_phases":prior["evidence_count"], "missing":prior["missing_phases"], "freeze_state":policy["authority"]["state"], "canonical_runtime_verified":False, "s20_s21_join_verified":False, "long_run_certified":False, "merge_authorized":False, "real_orders_authorized":False, "next":policy["next"]}

if __name__=="__main__":
    print(json.dumps(evaluate(),indent=2))

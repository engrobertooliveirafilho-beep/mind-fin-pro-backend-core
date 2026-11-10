"""R381: original Drive contract versus reconstructed candidate, fail-closed.

Drive artifact 1nLtELHloxFx7fIbTriITuND8xwhfhpLd is the historical
business.strategy_cashflow_agent implementation. Its run_dry returned
status=not_implemented, mode=stub. This audit does not claim equivalence.
"""
import ast
from mind_trader.experimental.et665_r380_identity_bound_execution import verify

ORIGINAL_DRIVE_ID="1nLtELHloxFx7fIbTriITuND8xwhfhpLd"
ORIGINAL_AGENT_ID="business.strategy_cashflow_agent"
ORIGINAL_RUN_DRY_SOURCE="""def run_dry(payload=None):
    return {
        "agent_id": AGENT_ID,
        "status": "not_implemented",
        "mode": "stub",
        "received": payload or {},
    }
"""

def classify_original(source):
    tree=ast.parse(source)
    runners=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="run_dry"]
    if len(runners)!=1:
        raise RuntimeError("original run_dry missing or ambiguous")
    values={}
    for node in ast.walk(runners[0]):
        if isinstance(node,ast.Dict):
            for key,value in zip(node.keys,node.values):
                if isinstance(key,ast.Constant) and isinstance(key.value,str) and isinstance(value,ast.Constant):
                    values[key.value]=value.value
    return {"status":values.get("status"),"mode":values.get("mode"),
            "stub":values.get("status")=="not_implemented" or values.get("mode")=="stub"}

def audit():
    original=classify_original(ORIGINAL_RUN_DRY_SOURCE)
    if not original["stub"]:
        raise RuntimeError("historical original stub evidence not reproduced")
    current=verify()
    matching=[p for p in current["proof"] if p["agent_id"]==ORIGINAL_AGENT_ID]
    if len(matching)!=1:
        raise RuntimeError("candidate original ID missing")
    return {"status":"ORIGINAL_STUB_RECONSTRUCTION_GAP_CONFIRMED",
            "historical_drive_id":ORIGINAL_DRIVE_ID,
            "historical_original":original,
            "reconstructed_candidate_output_sha256":matching[0]["output_sha256"],
            "reconstructed_candidate_processed":True,
            "original_functional_equivalence_verified":False,
            "official_hp19_certified":0,"phase_b_certified":0,
            "real_orders":"FORBIDDEN"}

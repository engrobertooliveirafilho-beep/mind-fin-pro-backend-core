"""R382: provenance comparison for two independently recovered historical agents.

Historical Drive sources:
business: 1nLtELHloxFx7fIbTriITuND8xwhfhpLd
cognition: 1pf58qy2-z_bzXtGIaC-y-4RlGPZZ5Znu
Both historical run_dry implementations returned not_implemented/stub.
"""
from importlib import import_module
from mind_trader.experimental.et665_r380_identity_bound_execution import verify

SOURCES={
 "business.strategy_cashflow_agent":{"drive_id":"1nLtELHloxFx7fIbTriITuND8xwhfhpLd","kind":"strategy_engine","step_count":11},
 "cognition.os_kernel_agent":{"drive_id":"1pf58qy2-z_bzXtGIaC-y-4RlGPZZ5Znu","kind":"cognitive_kernel","step_count":17},
}
def audit():
    report=verify()
    proof={p["agent_id"]:p for p in report["proof"]}
    comparisons=[]
    for agent_id,source in SOURCES.items():
        if agent_id not in proof:raise RuntimeError("missing reconstructed candidate")
        module=import_module(proof[agent_id]["module"])
        if getattr(module,"AGENT_ID",None)!=agent_id:raise RuntimeError("candidate identity mismatch")
        comparisons.append({"agent_id":agent_id,"historical_drive_id":source["drive_id"],
                            "historical_kind":source["kind"],
                            "historical_step_count":source["step_count"],
                            "historical_status":"not_implemented",
                            "historical_mode":"stub",
                            "reconstructed_output_sha256":proof[agent_id]["output_sha256"],
                            "reconstructed_executes":True,
                            "original_functional_equivalence_verified":False})
    return {"status":"TWO_HISTORICAL_STUB_GAPS_ATTESTED",
            "historical_sources_recovered":len(comparisons),
            "reconstructed_candidates_executed":report["candidate_executed"],
            "comparisons":comparisons,"official_hp19_certified":0,
            "phase_b_certified":0,"real_orders":"FORBIDDEN"}

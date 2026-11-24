from .p2408_paper_runtime_integration_gated import build_runtime

def audit(members, policy):
    runtime = build_runtime(members, policy)
    cases = [{}, {"symbol":"GER40","timeframe":"M15"},
             {"symbol":"XAUUSD"}, {"mode":"REAL"}, {"ftmo_real":True}]
    results = []
    for context in cases:
        result = runtime.dispatch(context)
        results.append({"context":context,"result":result,
                        "passed":result.get("allowed") is False
                        and result.get("real_execution_allowed") is False
                        and result.get("route") == "BLOCK"})
    return {"fault_checks":results,"quarantine_pass":all(r["passed"] for r in results),
            "final_certification":"BLOCKED","runtime_promotion_allowed":False,
            "real_execution_allowed":False,"ftmo_real_allowed":False}
